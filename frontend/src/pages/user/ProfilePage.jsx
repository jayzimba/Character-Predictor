import { useState } from 'react'
import { changePassword, updateProfile } from '../../api/auth'
import Field, { selectClass } from '../../components/public/Field'
import { useAuth } from '../../context/AuthContext'

export default function ProfilePage() {
  const { user, applyUser } = useAuth()
  const [profile, setProfile] = useState({
    first_name: user.first_name,
    last_name: user.last_name,
    gender: user.gender || '',
    age_group: user.age_group || '',
  })
  const [passwords, setPasswords] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  })
  const [profileMessage, setProfileMessage] = useState(null)
  const [profileError, setProfileError] = useState(null)
  const [passwordMessage, setPasswordMessage] = useState(null)
  const [passwordError, setPasswordError] = useState(null)
  const [profileBusy, setProfileBusy] = useState(false)
  const [passwordBusy, setPasswordBusy] = useState(false)

  function updateField(setter, field) {
    return (event) => setter((current) => ({ ...current, [field]: event.target.value }))
  }

  async function handleProfile(event) {
    event.preventDefault()
    setProfileBusy(true)
    setProfileError(null)
    setProfileMessage(null)
    try {
      const response = await updateProfile({
        first_name: profile.first_name,
        last_name: profile.last_name,
        gender: profile.gender || null,
        age_group: profile.age_group || null,
      })
      applyUser(response.data.data)
      setProfileMessage('Profile saved.')
    } catch (err) {
      setProfileError(err.response?.data?.message || 'Could not update profile.')
    } finally {
      setProfileBusy(false)
    }
  }

  async function handlePassword(event) {
    event.preventDefault()
    setPasswordBusy(true)
    setPasswordError(null)
    setPasswordMessage(null)
    try {
      await changePassword(passwords)
      setPasswords({ current_password: '', new_password: '', confirm_password: '' })
      setPasswordMessage('Password updated.')
    } catch (err) {
      setPasswordError(err.response?.data?.message || 'Could not change password.')
    } finally {
      setPasswordBusy(false)
    }
  }

  return (
    <div className="mx-auto max-w-3xl">
      <p className="text-sm font-medium text-teal">Account</p>
      <h1 className="mt-1 font-serif text-3xl text-ink">Profile</h1>
      <p className="mt-2 text-slate">
        Name and optional demographics only. Your role cannot be changed here.
      </p>

      <form className="mt-8 space-y-4 rounded-xl border border-line bg-card p-6" onSubmit={handleProfile}>
        <h2 className="font-serif text-xl text-ink">Details</h2>
        <p className="text-sm text-slate">{user.email}</p>
        <div className="grid gap-4 sm:grid-cols-2">
          <Field
            label="First name"
            value={profile.first_name}
            onChange={updateField(setProfile, 'first_name')}
            required
          />
          <Field
            label="Last name"
            value={profile.last_name}
            onChange={updateField(setProfile, 'last_name')}
            required
          />
        </div>
        <Field label="Gender (optional)">
          <select
            className={selectClass}
            value={profile.gender}
            onChange={updateField(setProfile, 'gender')}
          >
            <option value="">Prefer not to say</option>
            <option value="FEMALE">Female</option>
            <option value="MALE">Male</option>
            <option value="OTHER">Other</option>
            <option value="PREFER_NOT_TO_SAY">Prefer not to say</option>
          </select>
        </Field>
        <Field label="Age group (optional)">
          <select
            className={selectClass}
            value={profile.age_group}
            onChange={updateField(setProfile, 'age_group')}
          >
            <option value="">Prefer not to say</option>
            <option value="UNDER_18">Under 18</option>
            <option value="AGE_18_24">18–24</option>
            <option value="AGE_25_34">25–34</option>
            <option value="AGE_35_44">35–44</option>
            <option value="AGE_45_54">45–54</option>
            <option value="AGE_55_PLUS">55+</option>
          </select>
        </Field>
        {profileError && (
          <p className="text-sm text-red-800" role="alert">
            {profileError}
          </p>
        )}
        {profileMessage && <p className="text-sm text-teal">{profileMessage}</p>}
        <button
          type="submit"
          disabled={profileBusy}
          className="rounded-md bg-teal px-4 py-2.5 text-sm font-medium text-white hover:bg-teal-dark disabled:opacity-60"
        >
          {profileBusy ? 'Saving…' : 'Save profile'}
        </button>
      </form>

      <form className="mt-6 space-y-4 rounded-xl border border-line bg-card p-6" onSubmit={handlePassword}>
        <h2 className="font-serif text-xl text-ink">Password</h2>
        <Field
          label="Current password"
          type="password"
          value={passwords.current_password}
          onChange={updateField(setPasswords, 'current_password')}
          autoComplete="current-password"
          required
        />
        <Field
          label="New password"
          type="password"
          value={passwords.new_password}
          onChange={updateField(setPasswords, 'new_password')}
          autoComplete="new-password"
          required
        />
        <Field
          label="Confirm new password"
          type="password"
          value={passwords.confirm_password}
          onChange={updateField(setPasswords, 'confirm_password')}
          autoComplete="new-password"
          required
        />
        {passwordError && (
          <p className="text-sm text-red-800" role="alert">
            {passwordError}
          </p>
        )}
        {passwordMessage && <p className="text-sm text-teal">{passwordMessage}</p>}
        <button
          type="submit"
          disabled={passwordBusy}
          className="rounded-md bg-teal px-4 py-2.5 text-sm font-medium text-white hover:bg-teal-dark disabled:opacity-60"
        >
          {passwordBusy ? 'Updating…' : 'Update password'}
        </button>
      </form>
    </div>
  )
}
