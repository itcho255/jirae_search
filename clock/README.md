# Desktop Clock

간단한 윈도우 데스크톱 시계입니다. 화면 오른쪽 상단에 작게 표시되며 항상 위에 유지됩니다.

빠른 시작
- Python 3가 설치되어 있어야 합니다 (python 명령이 PATH에 있어야 편합니다).
- 터미널에서 실행:

```
python clock.py
```

자동 시작 등록
- `install_autostart.ps1` 스크립트를 관리자 권한 없이 PowerShell에서 실행하면 현재 사용자 로그인 시 자동으로 실행되는 바로가기를 생성합니다.
- PowerShell에서 스크립트 실행 예:

```powershell
cd "$(Split-Path -Path $MyInvocation.MyCommand.Definition -Parent)"
.\install_autostart.ps1
```

종료 및 사용법
- 오른쪽 클릭으로 앱을 종료할 수 있습니다.
- 왼쪽 버튼 드래그로 위치를 이동할 수 있습니다.

파일
- [clock.py](clock.py) : 메인 앱
- [install_autostart.ps1](install_autostart.ps1) : 자동 시작 바로가기 생성 스크립트
