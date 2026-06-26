# TransVideo installer build

This repo builds a Windows installer automatically with GitHub Actions.

## Manual build on Windows

```powershell
uv sync --locked
uv run pyinstaller --clean --noconfirm packaging/TransVideo.spec
choco install innosetup --yes
iscc packaging/installer.iss
```

The installer is created in `installer-dist/`.

## GitHub Actions

Open the `Build TransVideo Installer` workflow and run it manually, or push a tag:

```powershell
git tag v1.0-transvideo
git push origin v1.0-transvideo
```

The workflow uploads `TransVideo-Web-Setup-1.0.exe` as an artifact. Tag builds also attach it to a GitHub Release.
