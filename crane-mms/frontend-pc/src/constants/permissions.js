export const SETTINGS_PERMISSIONS = {
  EQUIPMENT_TEMPLATES_ACCESS: 'settings.equipment_templates.access',
  EQUIPMENT_TEMPLATES_GROUP_MANAGE: 'settings.equipment_templates.group.manage',
  EQUIPMENT_TEMPLATES_VERSION_MANAGE: 'settings.equipment_templates.version.manage',
  EQUIPMENT_TEMPLATES_CANDIDATES_REVIEW: 'settings.equipment_templates.candidates.review',
  EQUIPMENT_TEMPLATES_BASE_TEMPLATE_MANAGE: 'settings.equipment_templates.base_template.manage',
  EQUIPMENT_TEMPLATES_MODULE_TEMPLATES: 'settings.equipment_templates.module.templates',
  EQUIPMENT_TEMPLATES_MODULE_CANDIDATES: 'settings.equipment_templates.module.candidates',
  EQUIPMENT_TEMPLATES_MODULE_BASE_TEMPLATES: 'settings.equipment_templates.module.base_templates',

  PERMISSION_MANAGEMENT_ACCESS: 'settings.permission_management.access',
  PERMISSION_MANAGEMENT_ACCOUNT_CREATE: 'settings.permission_management.account.create',
  PERMISSION_MANAGEMENT_ACCOUNT_EDIT: 'settings.permission_management.account.edit',
  PERMISSION_MANAGEMENT_ACCOUNT_RESET_PASSWORD: 'settings.permission_management.account.reset_password',
  PERMISSION_MANAGEMENT_ACCOUNT_STATUS: 'settings.permission_management.account.status',
  PERMISSION_MANAGEMENT_DETAIL_VIEW: 'settings.permission_management.detail.view',
  PERMISSION_MANAGEMENT_ROLE_TEMPLATE_EDIT: 'settings.permission_management.role_template.edit',
  PERMISSION_MANAGEMENT_USER_OVERRIDE_EDIT: 'settings.permission_management.user_override.edit',
  PERMISSION_MANAGEMENT_MODULE_ROLE_DEFAULTS: 'settings.permission_management.module.role_defaults',
  PERMISSION_MANAGEMENT_MODULE_USER_OVERRIDES: 'settings.permission_management.module.user_overrides',
  PERMISSION_MANAGEMENT_MODULE_EFFECTIVE_PREVIEW: 'settings.permission_management.module.effective_preview',

  BRAND_CONFIG_ACCESS: 'settings.brand_config.access',
  BRAND_CONFIG_EDITOR_EDIT: 'settings.brand_config.editor.edit',
  BRAND_CONFIG_MODULE_EDITOR: 'settings.brand_config.module.editor',
  BRAND_CONFIG_MODULE_PREVIEW: 'settings.brand_config.module.preview',

  AUDIT_ACCESS: 'settings.audit.access',
  AUDIT_FILTERS_USE: 'settings.audit.filters.use',
  AUDIT_MODULE_LOGS: 'settings.audit.module.logs',
  AUDIT_MODULE_DETAIL: 'settings.audit.module.detail',

  REPORTS_ACCESS: 'settings.reports.access',
  REPORTS_DOWNLOAD: 'settings.reports.download',
  REPORTS_SIGNATURE_VIEW: 'settings.reports.signature.view',
  REPORTS_MODULE_ARCHIVE: 'settings.reports.module.archive'
}

export const ALL_SETTINGS_PERMISSION_KEYS = Object.values(SETTINGS_PERMISSIONS)

export const LEGACY_ROLE_PERMISSION_FALLBACK = {
  ADMIN: ALL_SETTINGS_PERMISSION_KEYS,
  MANAGER: [
    SETTINGS_PERMISSIONS.EQUIPMENT_TEMPLATES_ACCESS,
    SETTINGS_PERMISSIONS.EQUIPMENT_TEMPLATES_GROUP_MANAGE,
    SETTINGS_PERMISSIONS.EQUIPMENT_TEMPLATES_VERSION_MANAGE,
    SETTINGS_PERMISSIONS.EQUIPMENT_TEMPLATES_BASE_TEMPLATE_MANAGE,
    SETTINGS_PERMISSIONS.EQUIPMENT_TEMPLATES_MODULE_TEMPLATES,
    SETTINGS_PERMISSIONS.EQUIPMENT_TEMPLATES_MODULE_CANDIDATES,
    SETTINGS_PERMISSIONS.EQUIPMENT_TEMPLATES_MODULE_BASE_TEMPLATES,
    SETTINGS_PERMISSIONS.REPORTS_ACCESS,
    SETTINGS_PERMISSIONS.REPORTS_DOWNLOAD,
    SETTINGS_PERMISSIONS.REPORTS_SIGNATURE_VIEW,
    SETTINGS_PERMISSIONS.REPORTS_MODULE_ARCHIVE
  ],
  TECH: []
}
