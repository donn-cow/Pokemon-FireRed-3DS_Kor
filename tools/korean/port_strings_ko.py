#!/usr/bin/env python3
"""포트가 새로 넣은 문자열(한글판 롬에 없는 것)을 한국어로 바꾼다.

파티 경험치 메시지와 메가진화(이름, 특성, 도구, 전투 메시지)이다.
apply_korean_strings.py 다음에 실행한다.

    python port_strings_ko.py TREE
"""
import re
import sys
from pathlib import Path

MEGA_NAMES = {
    'Venusaur': '메가이상해꽃', 'CharizardX': '메가리자몽X', 'CharizardY': '메가리자몽Y',
    'Blastoise': '메가거북왕', 'Beedrill': '메가독침붕', 'Pidgeot': '메가피죤투',
    'Alakazam': '메가후딘', 'Slowbro': '메가야도란', 'Gengar': '메가팬텀',
    'Kangaskhan': '메가캥카', 'Pinsir': '메가쁘사이저', 'Gyarados': '메가갸라도스',
    'Aerodactyl': '메가프테라', 'MewtwoX': '메가뮤츠X', 'MewtwoY': '메가뮤츠Y',
    'Heracross': '메가헤라크로스', 'Dragonite': '메가망나뇽',
    'Ampharos': '메가전룡', 'Steelix': '메가강철톤', 'Scizor': '메가핫삼',
    'Houndoom': '메가헬가', 'Tyranitar': '메가마기라스', 'Sceptile': '메가나무킹',
    'Blaziken': '메가번치코', 'Swampert': '메가대짱이', 'Gardevoir': '메가가디안',
    'Sableye': '메가깜까미', 'Mawile': '메가입치트', 'Aggron': '메가보스로라',
    'Medicham': '메가요가램', 'Manectric': '메가썬더볼트', 'Sharpedo': '메가샤크니아',
    'Camerupt': '메가폭타', 'Altaria': '메가파비코리', 'Banette': '메가다크펫',
    'Absol': '메가앱솔', 'Glalie': '메가얼음귀신', 'Salamence': '메가보만다',
    'Metagross': '메가메타그로스', 'Latias': '메가라티아스', 'Latios': '메가라티오스',
    'Rayquaza': '메가레쿠쟈', 'Meganium': '메가메가니움', 'Feraligatr': '메가장크로다일',
    'Skarmory': '메가무장조', 'Clefable': '메가픽시', 'Victreebel': '메가우츠보트',
    'Starmie': '메가아쿠스타',
}

ABILITIES = {
    'ToughClaws': '단단한발톱', 'MegaLauncher': '메가런처', 'Adaptability': '적응력',
    'NoGuard': '노가드', 'ParentalBond': '부자유친', 'Aerilate': '스카이스킨',
    'MoldBreaker': '틀깨기', 'Steadfast': '불굴의마음', 'SkillLink': '스킬링크',
    'Multiscale': '멀티스케일', 'SandForce': '모래의힘', 'Technician': '테크니션',
    'SolarPower': '선파워', 'Pixilate': '페어리스킨', 'MagicBounce': '매직미러',
    'Filter': '필터', 'StrongJaw': '옹골찬턱', 'SheerForce': '우격다짐',
    'Prankster': '짓궂은마음', 'Refrigerate': '프리즈스킨', 'DeltaStream': '델타스트림',
    'MegaSol': '메가솔라', 'Dragonize': '드래곤스킨', 'Stalwart': '굳건한신념',
    'InnardsOut': '내용물분출',
}

ATK = '{B_ATK_NAME_WITH_PREFIX}'
SYMBOLS = {
    'src/battle_message.c': {
        'sText_PkmnTeamGainedEXP': '다른 포켓몬들도\\n경험치를 얻었다!\\p',
    },
    'src/battle_mega.c': {
        'sText_MegaStone': '메가스톤',
        'sText_MegaStoneY': '메가스톤Y',
        'sText_MegaRing': '메가링',
        'sDesc_MegaStone': '메가링을 가진 트레이너의\\n포켓몬이 지니면 배틀 중에\\n메가진화할 수 있다.',
        'sDesc_MegaRing': '키스톤이 박힌 팔찌.\\n메가스톤을 지닌 포켓몬이\\n한 배틀에 한 번 메가진화한다.',
        'sDesc_MegaStoneY': '메가스톤과 같지만 리자몽과\\n뮤츠를 Y의 모습으로\\n메가진화시킨다.',
        'sText_ReactingPlayer': ATK + '의 {B_LAST_ITEM}{JOSA_WA_GWA}\\n'
                                '{B_PLAYER_NAME}의 메가링이 반응했다!',
        'sText_ReactingFoe': ATK + '의 {B_LAST_ITEM}{JOSA_WA_GWA}\\n'
                             '{B_TRAINER1_NAME}의 메가링이 반응했다!',
        # 이름 뒤에 붙는다: "리자몽은\n메가리자몽X로 메가진화했다!"
        'sText_EvolvedInto': ATK + '{JOSA_EUN_NEUN}\\n',
        'sText_Exclamation': '{JOSA_EU}로 메가진화했다!',
        'sText_SolarPower': ATK + '{JOSA_EUN_NEUN}\\n선파워로 체력이 깎였다!',
        'sText_MagicBounce': ATK + '의 {B_CURRENT_MOVE}{JOSA_EUN_NEUN}\\n매직미러로 튕겨 나갔다!',
        'sText_DeltaStream': '정체불명의 난기류가\\n비행 포켓몬을 지키고 있다!',
    },
}
SYMBOLS['src/battle_mega.c'].update({'sName_' + k: v for k, v in MEGA_NAMES.items()})
SYMBOLS['src/battle_mega.c'].update({'sAbility_' + k: v for k, v in ABILITIES.items()})


def main():
    tree = Path(sys.argv[1])
    left = 0
    for rel, table in SYMBOLS.items():
        path = tree / rel
        text = path.read_text(encoding='utf-8')
        done = set()

        def sub(m):
            done.add(m.group(1))
            return '%s[] = _("%s");' % (m.group(1), table[m.group(1)])

        pat = re.compile(r'\b(%s)\[\] = _\("(?:[^"\\]|\\.)*"\);' % '|'.join(map(re.escape, table)))
        text = pat.sub(sub, text)
        path.write_text(text, encoding='utf-8', newline='\n')
        missing = sorted(set(table) - done)
        left += len(missing)
        print(rel, '바꿈', len(done), '못 찾음', missing)
    sys.exit(1 if left else 0)


if __name__ == '__main__':
    main()
