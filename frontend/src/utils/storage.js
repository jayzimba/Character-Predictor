const TOKEN_KEY = 'temperament.access_token'

export function getAccessToken() {
  return window.localStorage.getItem(TOKEN_KEY)
}

export function setAccessToken(token) {
  if (token) {
    window.localStorage.setItem(TOKEN_KEY, token)
    return
  }
  window.localStorage.removeItem(TOKEN_KEY)
}
