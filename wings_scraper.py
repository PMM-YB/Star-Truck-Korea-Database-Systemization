"""
WINGS 자동 다운로드 모듈
로컬 Chrome (WingsAutomation 프로필)을 이용해 WINGS Extended Search에서
Requested delivery date 조건으로 Excel 파일을 자동 다운로드합니다.

사용법:
    from wings_scraper import download_wings_excel
    path = download_wings_excel(["2026-04"], on_status=print)
    path = download_wings_excel(["2026-04", "2026-05"], on_status=print)
"""

import os
import asyncio
import tempfile

WINGS_URL = "https://wings.tsac.daimlertruck.com/sites/main.jsp"

# 전용 Chrome 프로필 디렉터리 (사용자의 메인 Chrome과 충돌 방지)
WINGS_PROFILE_DIR = os.path.join(
    os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
    "Google", "Chrome", "User Data", "WingsAutomation",
)


async def _wings_download_async(months: list, download_dir: str, on_status=None) -> str:
    from playwright.async_api import async_playwright

    months_sorted = sorted(months)
    start_date = months_sorted[0] + "-01"
    end_date = months_sorted[-1] + "-01"
    single = len(months_sorted) == 1

    os.makedirs(WINGS_PROFILE_DIR, exist_ok=True)
    os.makedirs(download_dir, exist_ok=True)

    def status(msg: str):
        if on_status:
            on_status(msg)

    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            WINGS_PROFILE_DIR,
            channel="chrome",
            headless=False,
            accept_downloads=True,
            downloads_path=download_dir,
            args=["--start-maximized"],
            no_viewport=True,
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        # ── 1. WINGS 접속 ──────────────────────────────────────────────────────
        status("WINGS에 접속 중...")
        await page.goto(WINGS_URL, wait_until="networkidle", timeout=30000)

        # 로그인이 필요한 경우 (WingsAutomation 프로필 첫 사용 시)
        if await page.locator("input[type='password']").count() > 0:
            status("로그인이 필요합니다. 브라우저에서 직접 로그인해 주세요...")
            await page.wait_for_selector("text=Extended search", timeout=180000)
            status("로그인 완료")

        # ── 2. Extended Search 진입 ────────────────────────────────────────────
        status("Extended Search 클릭 중...")
        await page.click("text=Extended search")
        await page.wait_for_load_state("networkidle", timeout=15000)

        # ── 3. 기존 필터 조건 제거 ────────────────────────────────────────────
        try:
            remove_btn = page.locator("text=Remove all filter criteria")
            if await remove_btn.is_visible(timeout=2000):
                await remove_btn.click()
                await page.wait_for_timeout(600)
        except Exception:
            pass

        # ── 4. 필터 조건 설정 ─────────────────────────────────────────────────
        status("필터 조건 설정 중...")
        if single:
            # 단일 월: Requested delivery date = equal = YYYY-MM-01
            await _set_filter_row(page, 0, "Requested delivery date", "equal", start_date)
        else:
            # 복수 월: >= start AND <= end
            await _set_filter_row(page, 0, "Requested delivery date", "greater equal", start_date)
            await page.click("text=New criteria")
            await page.wait_for_timeout(800)
            await _set_filter_row(page, 1, "Requested delivery date", "less equal", end_date)

        # ── 5. Execute 클릭 → 다운로드 대기 ──────────────────────────────────
        status("검색 실행 중... 파일 다운로드를 기다리는 중입니다.")
        async with page.expect_download(timeout=120000) as dl_info:
            await page.click("text=Execute")

        dl = await dl_info.value
        fname = dl.suggested_filename or f"wings_{start_date}_to_{end_date}.xlsx"
        fpath = os.path.join(download_dir, fname)
        await dl.save_as(fpath)

        status(f"다운로드 완료: {fname}")
        await ctx.close()
        return fpath


async def _set_filter_row(page, row_idx: int, field: str, operator: str, value: str):
    """필터 조건 행(row_idx번째)의 field / operator / value를 설정한다."""

    # ── field 드롭다운 찾기 ────────────────────────────────────────────────────
    # "Requested delivery date" 옵션을 포함하는 <select> 요소들 = field 드롭다운
    field_selects = page.locator("select").filter(
        has=page.locator("option", has_text="Requested delivery date")
    )
    count = await field_selects.count()

    if count > row_idx:
        fs = field_selects.nth(row_idx)
        await fs.select_option(label=field)

        # 같은 행(tr 또는 div) 내에서 operator select와 value input 찾기
        row_container = None
        for tag in ("tr", "div"):
            candidates = page.locator(tag).filter(has=fs)
            if await candidates.count() > 0:
                row_container = candidates.first
                break

        if row_container:
            # operator: "equal" 옵션을 포함하는 select
            op_sel = row_container.locator("select").filter(
                has=page.locator("option", has_text="equal")
            ).first
            if await op_sel.count() > 0:
                await op_sel.select_option(label=operator)

            # value: type='text' input
            val_inp = row_container.locator("input[type='text']").first
            if await val_inp.count() > 0:
                await val_inp.clear()
                await val_inp.fill(value)
            else:
                # fallback: 버튼/숨김 제외한 첫 번째 input
                val_inp2 = row_container.locator(
                    "input:not([type='button']):not([type='submit'])"
                    ":not([type='hidden']):not([type='checkbox'])"
                ).first
                if await val_inp2.count() > 0:
                    await val_inp2.clear()
                    await val_inp2.fill(value)
    else:
        # fallback: operator 드롭다운 및 text input을 페이지 전체에서 순서대로 사용
        op_selects = page.locator("select").filter(
            has=page.locator("option", has_text="greater equal")
        )
        if await op_selects.count() > row_idx:
            await op_selects.nth(row_idx).select_option(label=operator)

        text_inputs = page.locator("input[type='text']")
        if await text_inputs.count() > row_idx:
            await text_inputs.nth(row_idx).clear()
            await text_inputs.nth(row_idx).fill(value)


def download_wings_excel(months: list, download_dir: str = None, on_status=None) -> str:
    """
    WINGS에서 Excel 파일을 동기적으로 다운로드한다.

    Parameters
    ----------
    months : list of str
        'YYYY-MM' 형식의 생산월 리스트. 예: ['2026-04'] 또는 ['2026-04', '2026-05']
    download_dir : str, optional
        저장 디렉터리. None이면 임시 폴더 자동 생성.
    on_status : callable, optional
        진행 상황 콜백. on_status(str) 형태로 호출된다.

    Returns
    -------
    str
        다운로드된 파일의 절대 경로.
    """
    if not download_dir:
        download_dir = tempfile.mkdtemp(prefix="wings_dl_")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(
            _wings_download_async(months, download_dir, on_status)
        )
    finally:
        loop.close()
