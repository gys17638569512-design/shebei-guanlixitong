export function getPortalSession() {
  try {
    return JSON.parse(localStorage.getItem('portal_customer') || '{}')
  } catch (error) {
    return {}
  }
}

export function getPortalPermissions(session = getPortalSession()) {
  const accountType = session.account_type || 'CUSTOMER'
  const accountRole = session.account_role || (accountType === 'CUSTOMER' ? 'OWNER' : '')

  return {
    accountType,
    accountRole,
    canManageAccounts: accountType === 'CUSTOMER' || ['ADMIN', 'OWNER'].includes(accountRole),
    canSignOrders: accountType === 'CUSTOMER' || ['ADMIN', 'OWNER', 'SIGNER'].includes(accountRole),
    canEditSelfProfile: true,
    canChangeOwnPassword: accountType === 'CUSTOMER_ACCOUNT'
  }
}

export function clearPortalSession() {
  localStorage.removeItem('portal_token')
  localStorage.removeItem('portal_customer')
}
