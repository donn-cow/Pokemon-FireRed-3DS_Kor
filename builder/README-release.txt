포켓몬스터 파이어레드 3DS 한글판 (FireRed3DS-KO)
=================================================

포켓몬스터 파이어레드를 닌텐도 3DS에서 두 화면으로 즐기는 네이티브 포트
(FireRed3DS v0.5.2)를 한글판(K260613) 롬으로 실행할 수 있게 한 버전입니다.

이 배포본에는 게임이 들어 있지 않습니다. 본인이 가진 한글판 롬에서
빌더가 이 컴퓨터 안에서 게임 데이터를 만듭니다. 롬은 업로드되거나
복사·수정되지 않고, 인터넷 연결도 필요 없습니다(동행 포켓몬 이미지는 예외).

준비물
------
- 커스텀 펌웨어(Luma3DS)와 홈브류 런처가 설치된 3DS / 2DS 계열 기기
- 포켓몬스터 파이어레드 한글판 롬 (K260613)
    SHA-1 a79a61464f6b79d830af784969324945c5b73340
  일본판 롬(SHA-1 04139887b6cd8f53269aca098295b006ddba6cfe)에
  "20260613 포켓몬스터 파이어레드(J-K).xdelta"를 적용한 롬과 같습니다.
- 3DS의 SD 카드 (또는 직접 복사할 아무 폴더)

설치
----
1. 이 ZIP의 압축을 모두 풉니다.
2. FireRed3DS-Builder.exe 를 실행합니다.
3. 한글판 롬을 선택합니다. 지원하는 롬인지 빌더가 확인합니다.
4. SD 카드를 선택합니다("Nintendo 3DS" 폴더가 있으면 자동으로 찾습니다).
   아무 폴더를 선택해도 됩니다.
5. "설치"를 누릅니다. 다음 파일을 씁니다.
       /3ds/firered3ds-ko/FireRed3DS.3dsx
       /3ds/firered3ds-ko/FireRed3DS.smdh
       /3ds/firered3ds-ko/firered3ds.pak
6. SD 카드를 기기에 꽂고 홈브류 런처에서 "Pokemon FireRed 3DS KO"를 실행합니다.

홈 메뉴 아이콘 (CIA 포워더, 선택)
---------------------------------
FireRed3DS-KO-Forwarder.cia 를 FBI 등으로 설치하면 홈 메뉴에서 바로
실행할 수 있습니다. 포워더는 /3ds/firered3ds-ko/FireRed3DS.3dsx 를 실행하므로
게임을 업데이트할 때 CIA를 다시 설치할 필요가 없습니다.
영어판 FireRed3DS 포워더와 함께 설치할 수 있습니다.

세이브
------
세이브와 설정은 모두 /3ds/firered3ds-ko/ 폴더에 저장됩니다
(firered3ds.sav, settings.txt). 영어판(/3ds/firered3ds/)과 섞이지 않습니다.
다시 설치하거나 업데이트해도 세이브는 건드리지 않습니다.

알려진 제한
-----------
- 이름 입력 자판은 영문 배열입니다(미리 정해진 한글 이름은 고를 수 있습니다).
- 간이회화 가나다 모드의 글자 키는 자음 대신 첫 음절(가, 까, 나 …)로 표시합니다.
- 대사 글꼴(남자/여자 NPC)은 한글판 롬의 디자인을 그대로 따릅니다.

명령줄
------
    firered3ds-builder-cli.exe build   --rom "포켓몬스터 파이어레드 한글판.gba" --output out
    firered3ds-builder-cli.exe install --rom "포켓몬스터 파이어레드 한글판.gba" --sd E:\
    firered3ds-builder-cli.exe verify  --pak E:\3ds\firered3ds-ko\firered3ds.pak

법적 고지
---------
비공식 팬 프로젝트이며 Nintendo, Game Freak, Creatures, The Pokémon Company와
관계가 없고 승인받지 않았습니다. Pokémon과 Pokémon FireRed는 각 권리자의
상표입니다. 한글판 번역문과 그래픽은 이 배포본에 들어 있지 않고, 사용자의
롬에서만 만들어집니다. LICENSES/ 를 참고하세요.
