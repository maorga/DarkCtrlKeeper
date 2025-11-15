# Security Policy for DarkCtrlKeeper

## 🔒 For Users

### Downloading Safely

1. **Official Sources Only:**
   - Download only from official GitHub releases
   - URL: `https://github.com/maorga/DarkCtrlKeeper/releases`
   - Verify the repository owner before downloading

2. **Verify File Integrity:**
   - Check SHA256 checksums provided in release notes
   - Compare file size with documented size
   - Scan with antivirus software before running

3. **Administrator Privileges:**
   - DarkCtrlKeeper requests admin privileges for keyboard control
   - This is normal and required for global hotkeys
   - Windows UAC will prompt you - click "Yes"

### What Data is Collected?

- ✅ No data collected
- ✅ No network requests made
- ✅ Completely offline operation
- ❌ NO personal information
- ❌ NO file paths or system information
- ❌ NO keystroke data from user input
- ❌ NO game data or account information

### Antivirus False Positives

**Why it happens:**
- Keyboard control libraries are flagged as "keyloggers"
- PyInstaller executables are sometimes flagged as suspicious
- Admin privilege requirement raises flags

**How to verify safety:**
1. Download from official GitHub releases only
2. Check SHA256 hash matches release notes
3. Build from source yourself (see Building section)
4. Submit to VirusTotal for community analysis

**Whitelist in Windows Defender:**
```powershell
Add-MpPreference -ExclusionPath "C:\Path\To\DarkCtrlKeeper"
```

---

## 🛡️ For Developers

### CRITICAL: Configuration Management

1. **Use .gitignore:**
   - The provided `.gitignore` excludes sensitive files
   - Review before every commit:
     ```powershell
     git status
     git diff --cached
     ```

### Code Signing (Recommended for Releases)

To reduce antivirus false positives:

1. **Get a Code Signing Certificate:**
   - Purchase from SSL.com, DigiCert, or Sectigo
   - Cost: ~$100-500/year

2. **Sign the Executable:**
   ```powershell
   # Using signtool (Windows SDK)
   signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com /v DarkCtrlKeeper.exe
   ```

3. **Distribute Signed Binary:**
   - Signed executables are trusted by Windows
   - Reduces SmartScreen warnings
   - Fewer antivirus false positives

### Dependency Security

1. **Keep Dependencies Updated:**
   ```powershell
   # Check for updates
   pip list --outdated
   
   # Update specific package
   pip install --upgrade requests
   ```

2. **Audit Dependencies:**
   ```powershell
   # Check for known vulnerabilities
   pip install safety
   safety check
   ```

3. **Pin Versions in requirements.txt:**
   ```text
   # ✅ GOOD: Specific versions
   PyQt6==6.10.0
   pynput==1.7.6
   
   # ❌ BAD: Unpinned versions
   PyQt6
   pynput
   ```

### Secure Coding Practices

1. **Input Validation:**
   ```python
   # Always validate user input
   if not selected_number in ['4', '5']:
       raise ValueError("Invalid number selection")
   ```

2. **Error Handling:**
   ```python
   # Never expose sensitive info in errors
   try:
       load_config()
   except Exception as e:
       # ✅ GOOD: Generic message
       print("Configuration error")
       
       # ❌ BAD: Exposes file paths
       print(f"Failed to load {config_path}: {e}")
   ```

3. **Secure File Operations:**
   ```python
   # Use Path for cross-platform compatibility
   from pathlib import Path
   config_path = Path('user_config.json')
   
   # Set restrictive permissions (Windows)
   import os
   import stat
   os.chmod(config_path, stat.S_IRUSR | stat.S_IWUSR)
   ```

---

## 🐛 Reporting Vulnerabilities

### Responsible Disclosure

If you discover a security vulnerability:

1. **DO NOT** open a public GitHub issue
2. **DO** email the maintainer directly (provide email in README)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Response Timeline

- **24 hours:** Initial acknowledgment
- **7 days:** Assessment and triage
- **30 days:** Fix developed and tested
- **Release:** Patched version published
- **Disclosure:** Public disclosure after users have time to update

### Bug Bounty

Currently, no bug bounty program. Security researchers are credited in:
- Release notes
- SECURITY.md (this file)
- Hall of Fame section

---

## 🔐 Security Checklist for Contributors

Before submitting a pull request:

- [ ] No hardcoded secrets or sensitive data
- [ ] Dependencies pinned to specific versions
- [ ] Error messages don't leak sensitive information
- [ ] File operations use secure permissions
- [ ] Input validation for user-provided data
- [ ] Code reviewed for security vulnerabilities
- [ ] No debug code left in production

---

## 📚 Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [PyInstaller Security](https://pyinstaller.readthedocs.io/en/stable/usage.html#encrypting-python-bytecode)
- [GitHub Security Advisories](https://docs.github.com/en/code-security/security-advisories)

---

## 🏆 Security Hall of Fame

Contributors who have responsibly disclosed security issues:

*No security issues reported yet. Be the first!*

---

## 📜 License

DarkCtrlKeeper is released under the MIT License. See LICENSE file for details.

---

## ⚖️ Legal Disclaimer

DarkCtrlKeeper is provided "as is" without warranty of any kind. Use at your own risk. The developers are not responsible for:
- Damage to your system
- Interference with games or applications
- Violations of game terms of service
- Loss of data or game progress

Always review source code and understand what software does before running it with administrator privileges.

---

**Last Updated:** November 12, 2025  
**Security Contact:** (Add your email here)
