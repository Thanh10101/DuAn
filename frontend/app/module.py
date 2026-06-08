from components.auth import can_access_module, can_access_tab


OTHER_MODULE_KEY = "other"


MODULE_DEFINITIONS = [
    {
        "key": "qr",
        "title": "QR",
        "description": "Tạo và quản lý mã QR.",
        "icon": ":material/qr_code_2:",
    },
    {
        "key": "report",
        "title": "Báo cáo",
        "description": "Nhập, thống kê và xuất báo cáo công việc.",
        "icon": ":material/bar_chart:",
    },
    {
        "key": "mes",
        "title": "MES",
        "description": "Dữ liệu trạm và in QR MES.",
        "icon": ":material/precision_manufacturing:",
    },
    {
        "key": "bravo",
        "title": "Bravo",
        "description": "Đối chiếu dữ liệu Bravo.",
        "icon": ":material/rule:",
    },
]


OTHER_MODULE = {
    "key": OTHER_MODULE_KEY,
    "title": "Khác",
    "description": "Các chức năng chưa được gán module riêng.",
    "icon": ":material/apps:",
}


PAGES = [
    {
        "file": "pages/qr.py",
        "title": "Tạo QR",
        "icon": ":material/qr_code_2:",
        "module": "qr",
    },
    {
        "file": "pages/report_work.py",
        "title": "Báo cáo công việc",
        "icon": ":material/bar_chart:",
        "module": "report",
    },
    {
        "file": "pages/MES/get_station.py",
        "title": "Xuất dữ liệu trạm",
        "icon": ":material/table_view:",
        "module": "mes",
    },
    {
        "file": "pages/MES/qr_mes.py",
        "title": "In QR MES",
        "icon": ":material/print:",
        "module": "mes",
    },
    {
        "file": "pages/bravo/check.py",
        "title": "Đối chiếu",
        "icon": ":material/rule:",
        "module": "bravo",
    },
    {
        "file": "pages/login.py",
        "title": "Đăng nhập",
        "icon": ":material/login:",
        "module": None,
    },
    {
        "file": "pages/test.py",
        "title": "Test QR",
        "icon": ":material/experiment:",
        "module": None,
    },
    {
        "file": "pages/test_2.py",
        "title": "Test MES",
        "icon": ":material/science:",
        "module": None,
    },
    {
        "file": "pages/wifi_qr.py",
        "title": "wifi",
        "icon": ":material/science:",
        "module": None,
    },
]


def get_visible_modules(user_roles):
    module_by_key = {
        module["key"]: {
            **module,
            "pages": [],
        }
        for module in MODULE_DEFINITIONS
    }
    other_pages = []

    for page in PAGES:
        module_key = page.get("module") or OTHER_MODULE_KEY

        if not can_access_module(module_key, user_roles):
            continue

        if not can_access_tab(page["file"], user_roles):
            continue

        if module_key in module_by_key:
            module_by_key[module_key]["pages"].append(page)
        else:
            other_pages.append(page)

    visible_modules = [
        module_by_key[module["key"]]
        for module in MODULE_DEFINITIONS
        if module_by_key[module["key"]]["pages"]
    ]

    if other_pages:
        visible_modules.append({
            **OTHER_MODULE,
            "pages": other_pages,
        })

    return visible_modules


def get_module_by_key(modules, module_key):
    return next(
        (module for module in modules if module["key"] == module_key),
        None,
    )


def get_page_by_file(module, page_file):
    return next(
        (page for page in module["pages"] if page["file"] == page_file),
        None,
    )
