from models.user import RoleEnum


SETTINGS_PERMISSION_CATALOG = [
    {
        "module_key": "equipment_templates",
        "label": "设备模板中心",
        "route": "/equipment-templates",
        "groups": [
            {
                "group_key": "page",
                "label": "页面访问",
                "items": [
                    {"key": "settings.equipment_templates.access", "label": "进入设备模板中心", "type": "page"},
                ],
            },
            {
                "group_key": "actions",
                "label": "关键操作",
                "items": [
                    {"key": "settings.equipment_templates.group.manage", "label": "管理模板组", "type": "action"},
                    {"key": "settings.equipment_templates.version.manage", "label": "管理模板版本", "type": "action"},
                    {"key": "settings.equipment_templates.candidates.review", "label": "审核模板候选", "type": "action"},
                    {"key": "settings.equipment_templates.base_template.manage", "label": "管理检修通用模板", "type": "action"},
                ],
            },
            {
                "group_key": "modules",
                "label": "页面模块",
                "items": [
                    {"key": "settings.equipment_templates.module.templates", "label": "设备模板页签", "type": "module"},
                    {"key": "settings.equipment_templates.module.candidates", "label": "模板候选页签", "type": "module"},
                    {"key": "settings.equipment_templates.module.base_templates", "label": "检修通用模板页签", "type": "module"},
                ],
            },
        ],
    },
    {
        "module_key": "permission_management",
        "label": "权限管理",
        "route": "/system/employees",
        "groups": [
            {
                "group_key": "page",
                "label": "页面访问",
                "items": [
                    {"key": "settings.permission_management.access", "label": "进入权限管理", "type": "page"},
                ],
            },
            {
                "group_key": "actions",
                "label": "关键操作",
                "items": [
                    {"key": "settings.permission_management.account.create", "label": "新增账号", "type": "action"},
                    {"key": "settings.permission_management.account.edit", "label": "编辑账号", "type": "action"},
                    {"key": "settings.permission_management.account.reset_password", "label": "重置密码", "type": "action"},
                    {"key": "settings.permission_management.account.status", "label": "启停账号", "type": "action"},
                    {"key": "settings.permission_management.role_template.edit", "label": "编辑角色默认权限", "type": "action"},
                    {"key": "settings.permission_management.user_override.edit", "label": "编辑个人覆盖权限", "type": "action"},
                ],
            },
            {
                "group_key": "modules",
                "label": "页面模块",
                "items": [
                    {"key": "settings.permission_management.detail.view", "label": "员工详情权限面板", "type": "module"},
                    {"key": "settings.permission_management.module.role_defaults", "label": "角色默认权限区", "type": "module"},
                    {"key": "settings.permission_management.module.user_overrides", "label": "个人覆盖权限区", "type": "module"},
                    {"key": "settings.permission_management.module.effective_preview", "label": "生效权限预览区", "type": "module"},
                ],
            },
        ],
    },
    {
        "module_key": "brand_config",
        "label": "平台品牌配置",
        "route": "/system/brand-config",
        "groups": [
            {
                "group_key": "page",
                "label": "页面访问",
                "items": [
                    {"key": "settings.brand_config.access", "label": "进入平台品牌配置", "type": "page"},
                ],
            },
            {
                "group_key": "actions",
                "label": "关键操作",
                "items": [
                    {"key": "settings.brand_config.editor.edit", "label": "保存品牌配置", "type": "action"},
                ],
            },
            {
                "group_key": "modules",
                "label": "页面模块",
                "items": [
                    {"key": "settings.brand_config.module.editor", "label": "品牌编辑区", "type": "module"},
                    {"key": "settings.brand_config.module.preview", "label": "品牌预览区", "type": "module"},
                ],
            },
        ],
    },
    {
        "module_key": "audit",
        "label": "安全审计",
        "route": "/system/audit",
        "groups": [
            {
                "group_key": "page",
                "label": "页面访问",
                "items": [
                    {"key": "settings.audit.access", "label": "进入安全审计", "type": "page"},
                ],
            },
            {
                "group_key": "actions",
                "label": "关键操作",
                "items": [
                    {"key": "settings.audit.filters.use", "label": "使用筛选查询", "type": "action"},
                ],
            },
            {
                "group_key": "modules",
                "label": "页面模块",
                "items": [
                    {"key": "settings.audit.module.logs", "label": "日志列表区", "type": "module"},
                    {"key": "settings.audit.module.detail", "label": "日志详情弹窗", "type": "module"},
                ],
            },
        ],
    },
    {
        "module_key": "reports",
        "label": "报告集中",
        "route": "/system/reports",
        "groups": [
            {
                "group_key": "page",
                "label": "页面访问",
                "items": [
                    {"key": "settings.reports.access", "label": "进入报告集中", "type": "page"},
                ],
            },
            {
                "group_key": "actions",
                "label": "关键操作",
                "items": [
                    {"key": "settings.reports.download", "label": "下载 PDF 报告", "type": "action"},
                    {"key": "settings.reports.signature.view", "label": "查看电子签章凭证", "type": "action"},
                ],
            },
            {
                "group_key": "modules",
                "label": "页面模块",
                "items": [
                    {"key": "settings.reports.module.archive", "label": "归档报告列表区", "type": "module"},
                ],
            },
        ],
    },
]


def get_all_permission_keys() -> list[str]:
    keys: list[str] = []
    for module in SETTINGS_PERMISSION_CATALOG:
        for group in module["groups"]:
            for item in group["items"]:
                keys.append(item["key"])
    return sorted(keys)


ALL_SETTINGS_PERMISSION_KEYS = get_all_permission_keys()


DEFAULT_ROLE_PERMISSION_KEYS = {
    RoleEnum.ADMIN.value: ALL_SETTINGS_PERMISSION_KEYS,
    RoleEnum.MANAGER.value: [
        "settings.equipment_templates.access",
        "settings.equipment_templates.group.manage",
        "settings.equipment_templates.version.manage",
        "settings.equipment_templates.base_template.manage",
        "settings.equipment_templates.module.templates",
        "settings.equipment_templates.module.candidates",
        "settings.equipment_templates.module.base_templates",
        "settings.reports.access",
        "settings.reports.download",
        "settings.reports.signature.view",
        "settings.reports.module.archive",
    ],
    RoleEnum.TECH.value: [],
}


def get_default_permissions_for_role(role: str) -> list[str]:
    return list(DEFAULT_ROLE_PERMISSION_KEYS.get(role, []))
