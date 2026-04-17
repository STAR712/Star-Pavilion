from __future__ import annotations

from random import Random

from sqlalchemy.orm import Session

from auth_utils import hash_password
from models import Book, Bookshelf, Chapter, Conversation, User


BOOK_BLUEPRINTS = [
    {
        "title": "雾港回声",
        "author": "沈星遥",
        "category": "悬疑",
        "description": "暴雨季的临港旧城里，失踪案、旧码头与一段被篡改的口供重新浮出水面。调查记者许昼在追查真相时，发现每一次靠近答案，都会有人提前一步删去证据。",
        "protagonist": "许昼",
        "status": "连载中",
        "is_free": True,
    },
    {
        "title": "天穹织火录",
        "author": "顾临川",
        "category": "玄幻",
        "description": "边境熔城的少年在废墟下唤醒了失传多年的天火纹章，从此卷入宗门、王朝与古神残响的三重战场。每一次铸火，都是向命运讨回姓名。",
        "protagonist": "陆焰",
        "status": "连载中",
        "is_free": True,
    },
    {
        "title": "零度航线",
        "author": "林折光",
        "category": "科幻",
        "description": "深空回收船“北冕七号”在废弃跃迁带中捞起一枚失效舱体，舱内却躺着三十年前应该已经死亡的导航员。船长周岚由此卷入一场关于时间误差的宇宙事故。",
        "protagonist": "周岚",
        "status": "已完结",
        "is_free": False,
    },
    {
        "title": "长街见雪",
        "author": "程不渡",
        "category": "武侠",
        "description": "关中第一镖局覆灭后，唯一活下来的少镖头带着一柄断刀踏上归途。沿途每一场雪、每一间客栈、每一封无名信，都在提醒他当年的灭门案并未结束。",
        "protagonist": "谢衡",
        "status": "连载中",
        "is_free": True,
    },
    {
        "title": "云上春信",
        "author": "纪南歌",
        "category": "轻小说",
        "description": "转学第一天，夏栀误闯旧校舍广播室，收到一卷写着未来日期的磁带。从那以后，校园里每一个平静的日常，都开始藏着一点点会改变命运的回音。",
        "protagonist": "夏栀",
        "status": "连载中",
        "is_free": True,
    },
    {
        "title": "长安夜行备忘录",
        "author": "燕归迟",
        "category": "历史",
        "description": "大雍京城深夜连续发生离奇火案，低阶史官沈既白被迫协助查案。他本想明哲保身，却在案卷夹层里看见一行被故意抹去的旧字，从此一步步走入朝堂暗潮。",
        "protagonist": "沈既白",
        "status": "已完结",
        "is_free": True,
    },
    {
        "title": "城市失焦面",
        "author": "周闻笙",
        "category": "都市",
        "description": "商业摄影师许意在一次拍摄事故后，发现自己的镜头总能提前捕捉到他人即将失控的一瞬。她原以为这是好运，直到那些画面开始和一桩多年旧案重叠。",
        "protagonist": "许意",
        "status": "连载中",
        "is_free": False,
    },
    {
        "title": "扶风问月",
        "author": "江照白",
        "category": "仙侠",
        "description": "下山试炼的外门弟子裴照在古祠中捡到一面会在月下说话的铜镜。镜中人自称曾见过九重天崩塌的那一夜，而裴照恰好是那场旧劫唯一剩下的钥匙。",
        "protagonist": "裴照",
        "status": "连载中",
        "is_free": True,
    },
]

CHAPTER_LEXICON = {
    "悬疑": ["雨夜来信", "码头回声", "停摆钟楼", "无人的证词", "灰仓门后", "倒放录像", "第三条航道", "雾里的名字"],
    "玄幻": ["炉火开纹", "古殿潮音", "焰骨试炼", "夜渡王庭", "碎星长桥", "赤金战帖", "天井回响", "山门鸣钟"],
    "科幻": ["冷舱苏醒", "航标偏移", "寂静坐标", "回收指令", "镜像星图", "零度折返", "深空盲区", "最终靠泊"],
    "武侠": ["客栈灯寒", "断刀上路", "雪巷旧识", "桥边试锋", "夜泊江声", "雨中拜帖", "北地追骑", "长街决意"],
    "轻小说": ["广播室的磁带", "被改写的值日表", "天台借风", "夏祭前夜", "雨停之后", "误点发送", "操场回音", "春信抵达"],
    "历史": ["更鼓未尽", "旧档残页", "坊门熄灯", "宫墙夜火", "朱笔改句", "御街追影", "春官旧案", "长安初雪"],
    "都市": ["镜头偏差", "高架晚风", "空白底片", "深夜片场", "失焦来电", "楼顶访客", "反光玻璃", "重拍那一夜"],
    "仙侠": ["月下古镜", "山门薄雾", "祠中灵息", "夜半问剑", "风起灵舟", "旧劫残页", "云海试心", "照月归途"],
}

SCENE_LEXICON = {
    "悬疑": ["潮湿的旧码头", "被雨雾遮住的仓储街", "只亮着半盏灯的值班室", "信号时断时续的防波堤"],
    "玄幻": ["熔城外侧的黑色火脉", "仍残留古神刻痕的山门石阶", "被风雪封住的试炼长廊", "翻涌着热浪的天井战台"],
    "科幻": ["舷窗外缓慢翻转的空间碎屑", "低温回收舱泛蓝的冷光", "导航室不断闪烁的故障提示", "跃迁带边缘漂移的废弃浮标"],
    "武侠": ["积雪未融的北地长街", "河风猎猎的旧渡口", "茶烟袅袅的驿路客栈", "刀光照亮又迅速熄灭的小巷"],
    "轻小说": ["午后无人使用的广播室", "飘着粉笔灰的旧走廊", "风一吹就会发出轻响的天台门", "被夕阳染成橘色的操场看台"],
    "历史": ["更夫刚走过的坊门口", "积着纸灰和烛油的案牍房", "雨后尚未清扫的御街石面", "连宫灯都压低火色的偏殿长廊"],
    "都市": ["灯牌倒映在玻璃幕墙上的街口", "凌晨仍在运作的摄影棚", "被风吹得发响的高架桥下", "空无一人的商场连廊"],
    "仙侠": ["月色淌过的山门古阶", "灵气稀薄却格外安静的旧祠", "悬在云海上的渡桥", "钟声传得很远的后山道场"],
}

EMOTION_LEXICON = ["不安", "迟疑", "倔强", "克制", "警觉", "笃定", "疲惫", "清醒"]
TURN_LEXICON = ["线索忽然对上了缺口", "沉默的人终于给出了回应", "看似平静的局面出现了裂痕", "一条被忽视的细节突然有了重量"]
ENDING_LEXICON = ["真正的麻烦还没有开始。", "这一夜留下的余波，注定会在下一章掀开更大的局。", "他知道自己已经不可能再回到原来的位置。", "答案没有立刻出现，但命运已经先迈出一步。"]


def _generate_chapter_content(
    rng: Random,
    blueprint: dict,
    chapter_title: str,
    chapter_number: int,
) -> str:
    protagonist = blueprint["protagonist"]
    scene = rng.choice(SCENE_LEXICON[blueprint["category"]])
    emotion = rng.choice(EMOTION_LEXICON)
    turn = rng.choice(TURN_LEXICON)
    ending = rng.choice(ENDING_LEXICON)

    paragraphs = [
        (
            f"第{chapter_number}章《{chapter_title}》从{scene}开始。{protagonist}原本只想把眼前这件事处理干净，"
            f"却在抬头的一瞬间意识到，自己正被更大的局势缓慢推着向前。空气里有一种说不清的{emotion}，"
            f"像是有人提前写好了这一章的开场，只等他亲自走进来。"
        ),
        (
            f"{blueprint['description']}这一层背景，在这一章里不再只是远处的设定，而是带着温度和压力压到{protagonist}身上。"
            f"他仔细回想前一段时间留下的每一个细节，发现那些曾被忽略的停顿、眼神和空白，"
            f"其实都在悄悄指向同一个方向。"
        ),
        (
            f"事情的推进并不猛烈，反而带着一种绵密的逼近感。{protagonist}与身边人的对话看似平静，"
            f"但每一句都在试探边界；每一个转身都像在替下一次冲突蓄力。等到{turn}时，"
            f"他才明白，原来自己一直站在门槛上，只差半步就会踩进真正的核心。"
        ),
        (
            f"这一章最重要的不是胜负，而是选择。{protagonist}没有立刻交出答案，"
            f"只是把掌心收紧，记住了眼前的人、风里的味道，以及那句差点被掩过去的话。"
            f"他很清楚，下一次再遇到同样的局面，自己必须给出比今天更锋利的回应。"
        ),
        (
            f"夜色或晨光在这一段结尾里缓慢退开，{protagonist}终于把线索、情绪与行动拼成了一个新的轮廓。"
            f"{ending}"
        ),
    ]
    return "\n\n".join(paragraphs)


USER_BLUEPRINTS = [
    {"username": "admin", "password": "123", "role": "admin"},
    {"username": "书虫小明", "password": "123456", "role": "reader"},
    {"username": "阅读达人", "password": "123456", "role": "reader"},
]


def _ensure_users(db: Session) -> None:
    for blueprint in USER_BLUEPRINTS:
        user = db.query(User).filter(User.username == blueprint["username"]).first()
        if user is None:
            user = User(
                username=blueprint["username"],
                password_hash=hash_password(blueprint["password"]),
                role=blueprint["role"],
                avatar="",
            )
            db.add(user)
            continue

        changed = False
        if not user.password_hash:
            user.password_hash = hash_password(blueprint["password"])
            changed = True
        if user.role != blueprint["role"]:
            user.role = blueprint["role"]
            changed = True
        if changed:
            db.add(user)

    db.commit()


def ensure_demo_data(db: Session, force: bool = False) -> dict[str, int | bool]:
    if force:
        db.query(Bookshelf).delete()
        db.query(Conversation).delete()
        db.query(Chapter).delete()
        db.query(Book).delete()
        db.query(User).delete()
        db.commit()

    _ensure_users(db)

    existing_books = db.query(Book).count()
    if existing_books > 0:
        return {
            "created": False,
            "books": existing_books,
            "chapters": db.query(Chapter).count(),
            "bookshelf": db.query(Bookshelf).count(),
        }

    rng = Random(20260416)
    book_ids: list[int] = []

    for index, blueprint in enumerate(BOOK_BLUEPRINTS, start=1):
        chapter_titles = CHAPTER_LEXICON[blueprint["category"]]
        chapter_total = rng.randint(6, 8)
        selected_titles = chapter_titles[:chapter_total]

        book = Book(
            title=blueprint["title"],
            author=blueprint["author"],
            category=blueprint["category"],
            description=blueprint["description"],
            status=blueprint["status"],
            is_free=blueprint["is_free"],
            read_count=rng.randint(80_000, 980_000),
            recommend_count=rng.randint(8_000, 120_000),
            cover_url="",
        )
        db.add(book)
        db.flush()
        book_ids.append(book.id)

        total_words = 0
        for chapter_number, chapter_title in enumerate(selected_titles, start=1):
            content = _generate_chapter_content(
                rng=rng,
                blueprint=blueprint,
                chapter_title=chapter_title,
                chapter_number=chapter_number,
            )
            total_words += len(content)
            db.add(
                Chapter(
                    book_id=book.id,
                    chapter_number=chapter_number,
                    title=f"第{chapter_number}章 {chapter_title}",
                    content=content,
                    word_count=len(content),
                )
            )

        book.word_count = total_words

    db.commit()

    admin_user = db.query(User).filter(User.username == "admin").first()
    if admin_user is None:
        raise RuntimeError("管理员账号初始化失败")

    sample_books = book_ids[:4]
    db.add_all(
        [
            Bookshelf(user_id=admin_user.id, book_id=sample_books[0], current_chapter=2, progress=28.0),
            Bookshelf(user_id=admin_user.id, book_id=sample_books[1], current_chapter=1, progress=12.0),
            Bookshelf(user_id=admin_user.id, book_id=sample_books[2], current_chapter=4, progress=61.0),
        ]
    )
    db.commit()

    return {
        "created": True,
        "books": db.query(Book).count(),
        "chapters": db.query(Chapter).count(),
        "bookshelf": db.query(Bookshelf).count(),
    }
