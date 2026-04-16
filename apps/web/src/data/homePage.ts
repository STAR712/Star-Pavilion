export type GenreKey =
  | '玄幻'
  | '奇幻'
  | '武侠'
  | '仙侠'
  | '都市'
  | '历史'
  | '科幻'
  | '悬疑'
  | '游戏'
  | '轻小说'

export interface GenreMeta {
  key: GenreKey
  glyph: string
  tagline: string
  description: string
  count: number
  accent: string
  surface: string
  coverColors: [string, string, string]
}

export interface HomeBook {
  id: string
  title: string
  author: string
  genre: GenreKey
  summary: string
  hook: string
  chapterTitle: string
  wordCount: number
  heat: number
  recommend: number
  ticket: number
  score: number
  freshScore: number
  cover: string
  accent: string
  status: '连载中' | '已完结'
  tags: string[]
}

export interface HeroSlide {
  id: string
  genre: GenreKey
  title: string
  lead: string
  summary: string
  chapterTitle: string
  tags: string[]
  stats: Array<{ label: string; value: number }>
  cover: string
  accent: string
}

export interface PromoCard {
  id: string
  title: string
  caption: string
  detail: string
  accent: string
  cover: string
  genre: GenreKey
}

export interface RankingBoard {
  id: string
  title: string
  subtitle: string
  accent: string
  books: HomeBook[]
}

export interface GenreShelf {
  id: string
  title: string
  glyph: string
  accent: string
  note: string
  books: HomeBook[]
}

export interface UpdateItem {
  id: string
  genre: GenreKey
  title: string
  chapterTitle: string
  author: string
  time: string
  badge: string
}

export interface AuthorSpotlight {
  id: string
  name: string
  title: string
  summary: string
  works: string[]
  accent: string
  initials: string
}

export interface HomePageData {
  genres: GenreMeta[]
  allBooks: HomeBook[]
  heroSlides: HeroSlide[]
  promoCards: PromoCard[]
  hotSpotlight: HomeBook
  hotBooks: HomeBook[]
  rankingBoards: RankingBoard[]
  shelves: GenreShelf[]
  updates: UpdateItem[]
  authorSpotlights: AuthorSpotlight[]
  newReleases: HomeBook[]
  freeReading: HomeBook[]
}

type GenreLexicon = {
  prefixes: string[]
  suffixes: string[]
  roles: string[]
  scenes: string[]
  powers: string[]
  chapterFirst: string[]
  chapterSecond: string[]
  tags: string[]
}

const genreDefinitions: GenreMeta[] = [
  {
    key: '玄幻',
    glyph: '玄',
    tagline: '星河问道',
    description: '万族争锋，古域长燃',
    count: 721226,
    accent: '#4b64f5',
    surface: 'linear-gradient(135deg, rgba(75, 100, 245, 0.18), rgba(255, 255, 255, 0.95))',
    coverColors: ['#172554', '#355cdd', '#b9c7ff'],
  },
  {
    key: '奇幻',
    glyph: '幻',
    tagline: '秘境龙歌',
    description: '王座、秘环与巨龙残卷',
    count: 159482,
    accent: '#8b5cf6',
    surface: 'linear-gradient(135deg, rgba(139, 92, 246, 0.18), rgba(255, 255, 255, 0.95))',
    coverColors: ['#312e81', '#7c3aed', '#ddd6fe'],
  },
  {
    key: '武侠',
    glyph: '武',
    tagline: '刀锋夜雪',
    description: '山河入局，快意恩仇',
    count: 45491,
    accent: '#cf5d2c',
    surface: 'linear-gradient(135deg, rgba(207, 93, 44, 0.18), rgba(255, 255, 255, 0.95))',
    coverColors: ['#7c2d12', '#c2410c', '#fed7aa'],
  },
  {
    key: '仙侠',
    glyph: '仙',
    tagline: '云海飞升',
    description: '洞天、仙门与长生棋局',
    count: 236714,
    accent: '#0f8b8d',
    surface: 'linear-gradient(135deg, rgba(15, 139, 141, 0.18), rgba(255, 255, 255, 0.95))',
    coverColors: ['#134e4a', '#0f766e', '#99f6e4'],
  },
  {
    key: '都市',
    glyph: '都',
    tagline: '霓虹逆袭',
    description: '财富、悬案与夜色博弈',
    count: 375018,
    accent: '#dc5b4f',
    surface: 'linear-gradient(135deg, rgba(220, 91, 79, 0.18), rgba(255, 255, 255, 0.95))',
    coverColors: ['#7f1d1d', '#dc2626', '#fecaca'],
  },
  {
    key: '历史',
    glyph: '史',
    tagline: '长安折戟',
    description: '帝国兴替，边关风雪',
    count: 77285,
    accent: '#b7812b',
    surface: 'linear-gradient(135deg, rgba(183, 129, 43, 0.18), rgba(255, 255, 255, 0.95))',
    coverColors: ['#78350f', '#b45309', '#fde68a'],
  },
  {
    key: '科幻',
    glyph: '科',
    tagline: '量子远航',
    description: '深空信号与文明余烬',
    count: 157640,
    accent: '#2082d8',
    surface: 'linear-gradient(135deg, rgba(32, 130, 216, 0.18), rgba(255, 255, 255, 0.95))',
    coverColors: ['#082f49', '#0369a1', '#bae6fd'],
  },
  {
    key: '悬疑',
    glyph: '悬',
    tagline: '迷雾访客',
    description: '旧案回潮，夜幕追凶',
    count: 66942,
    accent: '#5b6476',
    surface: 'linear-gradient(135deg, rgba(91, 100, 118, 0.18), rgba(255, 255, 255, 0.95))',
    coverColors: ['#111827', '#374151', '#d1d5db'],
  },
  {
    key: '游戏',
    glyph: '游',
    tagline: '满级开服',
    description: '天梯、团本与职业觉醒',
    count: 108902,
    accent: '#15803d',
    surface: 'linear-gradient(135deg, rgba(21, 128, 61, 0.18), rgba(255, 255, 255, 0.95))',
    coverColors: ['#14532d', '#16a34a', '#bbf7d0'],
  },
  {
    key: '轻小说',
    glyph: '轻',
    tagline: '青春共振',
    description: '校园、恋爱与异想日常',
    count: 113768,
    accent: '#ec4899',
    surface: 'linear-gradient(135deg, rgba(236, 72, 153, 0.18), rgba(255, 255, 255, 0.95))',
    coverColors: ['#831843', '#db2777', '#fbcfe8'],
  },
]

const genreLexicon: Record<GenreKey, GenreLexicon> = {
  玄幻: {
    prefixes: ['九霄', '太初', '星渊', '荒天', '帝阙', '神墟'],
    suffixes: ['问道', '帝途', '天骄', '战录', '长歌', '神谕'],
    roles: ['外门弟子', '古族弃子', '守塔少年', '无名药师'],
    scenes: ['诸天战场', '古神遗迹', '苍穹断层', '星陨古城'],
    powers: ['星骨', '古印', '焚天血脉', '万象灵根'],
    chapterFirst: ['破晓', '焚天', '归潮', '启星', '逆骨', '古塔'],
    chapterSecond: ['之战', '试炼', '回响', '问心', '惊雷', '开门'],
    tags: ['热血', '升级', '宗门', '群像'],
  },
  奇幻: {
    prefixes: ['龙裔', '秘环', '霜境', '夜辉', '群岛', '银月'],
    suffixes: ['秘典', '纪元', '王庭', '旅歌', '圣痕', '回响'],
    roles: ['流浪学徒', '王庭译员', '失语骑士', '炼金见习生'],
    scenes: ['北境王都', '浮空群岛', '龙眠峡湾', '永夜钟塔'],
    powers: ['龙语印记', '秘银心核', '月潮祝祷', '群星符文'],
    chapterFirst: ['龙火', '冰湖', '群塔', '王座', '密约', '远征'],
    chapterSecond: ['苏醒', '誓言', '回信', '决议', '夜巡', '交锋'],
    tags: ['冒险', '魔法', '龙族', '异域'],
  },
  武侠: {
    prefixes: ['雪刃', '江湖', '青锋', '长街', '落梅', '沧浪'],
    suffixes: ['刀客行', '剑雨录', '夜行簿', '山河令', '旧梦谣', '风云渡'],
    roles: ['无名刀客', '客栈掌柜', '落魄少主', '药谷弟子'],
    scenes: ['雁门雪夜', '洛水长街', '塞外驿站', '残灯渡口'],
    powers: ['断水十三式', '藏锋心法', '听雪剑意', '无影步'],
    chapterFirst: ['断桥', '夜雪', '酒肆', '山雨', '寒灯', '孤城'],
    chapterSecond: ['约战', '听风', '换盏', '折剑', '追命', '封刀'],
    tags: ['江湖', '群像', '快意', '权谋'],
  },
  仙侠: {
    prefixes: ['云海', '灵墟', '青冥', '玉京', '太乙', '沧溟'],
    suffixes: ['飞升录', '问心篇', '道庭', '仙门纪', '长生路', '渡劫书'],
    roles: ['守山弟子', '失格仙君', '符师少女', '渡船少年'],
    scenes: ['云海天门', '归墟渡口', '万象洞天', '太微道场'],
    powers: ['青冥剑骨', '九转元炁', '太虚符种', '天河命盘'],
    chapterFirst: ['灵潮', '道钟', '飞舟', '玉简', '落星', '天河'],
    chapterSecond: ['入梦', '问罪', '回山', '照影', '试道', '开坛'],
    tags: ['修仙', '渡劫', '仙门', '长生'],
  },
  都市: {
    prefixes: ['霓虹', '重返', '财团', '夜幕', '旧城', '顶流'],
    suffixes: ['回响', '纪事', '逆袭', '法则', '猎场', '开局'],
    roles: ['被裁高管', '实习律师', '夜班医生', '落魄投资人'],
    scenes: ['CBD 顶层会议室', '江岸旧厂区', '午夜直播间', '海滨金融街'],
    powers: ['超忆推演', '风险视界', '谈判天赋', '反诈直觉'],
    chapterFirst: ['签字', '追查', '布局', '夜谈', '反击', '破局'],
    chapterSecond: ['时刻', '会议', '底牌', '交易', '回线', '出手'],
    tags: ['逆袭', '创业', '悬案', '群像'],
  },
  历史: {
    prefixes: ['长安', '大秦', '边关', '盛唐', '燕云', '河洛'],
    suffixes: ['旧事', '策', '烽火', '夜行', '长歌', '折简'],
    roles: ['寒门书生', '边军校尉', '落魄宗室', '女史官'],
    scenes: ['雁门关外', '长安西市', '洛阳行台', '河西军帐'],
    powers: ['兵书残卷', '河图密诏', '惊鸿骑术', '观天算筹'],
    chapterFirst: ['边鼓', '雪夜', '诏书', '城门', '夜宴', '渡河'],
    chapterSecond: ['惊变', '起程', '定策', '闻鼓', '封关', '折返'],
    tags: ['朝堂', '争霸', '家国', '权谋'],
  },
  科幻: {
    prefixes: ['量子', '深空', '星舰', '矩阵', '黎明', '零号'],
    suffixes: ['边境', '协议', '远航', '纪元', '回路', '回声'],
    roles: ['轨道工程师', '记忆考古员', '舰队副官', '仿生修复师'],
    scenes: ['木卫三轨道城', '深空航道', '文明废墟层', '地月同步港'],
    powers: ['折跃模组', '神经镜像', '零域算法', '量子骨骼'],
    chapterFirst: ['折跃', '封舱', '信标', '熄灯', '外环', '失重'],
    chapterSecond: ['预案', '呼叫', '对接', '回收', '警报', '接管'],
    tags: ['星际', '机甲', 'AI', '文明'],
  },
  悬疑: {
    prefixes: ['迷雾', '旧案', '暗河', '白昼', '镜夜', '无声'],
    suffixes: ['访客', '档案', '追凶簿', '证词', '回线', '现场'],
    roles: ['刑侦顾问', '法医新人', '失眠记者', '测谎分析师'],
    scenes: ['雨夜高架桥', '旧城档案室', '废弃钟楼', '临江码头'],
    powers: ['微表情推演', '记忆还原', '听觉追踪', '现场重构'],
    chapterFirst: ['封锁', '失踪', '证物', '回访', '夜勘', '反证'],
    chapterSecond: ['名单', '时差', '残页', '回声', '盲区', '来信'],
    tags: ['破案', '反转', '高智', '群像'],
  },
  游戏: {
    prefixes: ['满级', '天梯', '职业', '团本', '开服', '神装'],
    suffixes: ['开局', '重启', '纪要', '王座', '觉醒', '日志'],
    roles: ['战队分析师', '散人玩家', '副本指挥', '天赋测试员'],
    scenes: ['跨服总决赛', '遗迹团本', '新版本赛季', '全息训练舱'],
    powers: ['全图意识', '稀有模板', '战术模拟', '无限连携'],
    chapterFirst: ['开荒', '越塔', '连胜', '团灭', '决赛', '补刀'],
    chapterSecond: ['节点', '翻盘', '起手', '抢龙', '读秒', '复盘'],
    tags: ['电竞', '系统', '升级', '热血'],
  },
  轻小说: {
    prefixes: ['同桌', '社团', '夏日', '放学后', '便利店', '星见'],
    suffixes: ['手册', '日记', '物语', '回信', '社', '失眠夜'],
    roles: ['转校生', '社团经理', '图书委员', '游戏主播少女'],
    scenes: ['放学后的旧社团教室', '海边合宿旅馆', '深夜便利店', '樱花坡天台'],
    powers: ['情绪共振', '梦境留言', '时间暂停三分钟', '幸运剧本'],
    chapterFirst: ['约会', '雨夜', '天台', '合宿', '星光', '心跳'],
    chapterSecond: ['误差', '来信', '换位', '试探', '回放', '和解'],
    tags: ['校园', '恋爱', '治愈', '幻想'],
  },
}

const authorSurnames = ['沈', '顾', '林', '裴', '闻', '苏', '陆', '谢', '秦', '韩', '季', '周', '温', '许']
const authorGivenFirst = ['砚', '舟', '川', '岚', '叙', '衡', '野', '遥', '照', '衍', '宁', '青']
const authorGivenSecond = ['之', '川', '舟', '歌', '野', '宁', '岑', '序', '行', '远', '白', '言']
const authorTitleSuffix = ['', '', '', '客']
const statusPool: Array<'连载中' | '已完结'> = ['连载中', '连载中', '连载中', '已完结']
const hookPool = ['热议攀升', '口碑发酵', '追更狂飙', '编辑热推', '评论区高能', '榜单常驻']
const updateBadges = ['新更', '热评', '飙升', '主编荐', '高能']
const rankingDefinitions = [
  { id: 'tickets', title: '月票榜', subtitle: 'VIP 新作', accent: '#b43b2d', metric: 'ticket' as const },
  { id: 'hot', title: '畅销榜', subtitle: '热读狂飙', accent: '#d27a2c', metric: 'heat' as const },
  { id: 'score', title: '书友榜', subtitle: '口碑精选', accent: '#3d63e0', metric: 'score' as const },
  { id: 'read', title: '阅读指数榜', subtitle: '全站追更', accent: '#187b64', metric: 'recommend' as const },
  { id: 'fresh', title: '签约作者新书榜', subtitle: '新书高光', accent: '#8a47db', metric: 'freshScore' as const },
]

const shelfDefinitions = [
  { id: 'xuanqi', title: '玄幻 · 奇幻', glyph: '玄', accent: '#4b64f5', genres: ['玄幻', '奇幻'] as GenreKey[], note: '宏大世界与冒险奇观' },
  { id: 'wuxian', title: '武侠 · 仙侠', glyph: '仙', accent: '#0f8b8d', genres: ['武侠', '仙侠'] as GenreKey[], note: '山河刀影与修真长夜' },
  { id: 'urban', title: '都市 · 历史', glyph: '策', accent: '#dc5b4f', genres: ['都市', '历史'] as GenreKey[], note: '现实逆袭与家国权谋' },
  { id: 'future', title: '科幻 · 悬疑', glyph: '谜', accent: '#2082d8', genres: ['科幻', '悬疑'] as GenreKey[], note: '未知文明与迷案回潮' },
  { id: 'game', title: '游戏 · 轻小说', glyph: '游', accent: '#15803d', genres: ['游戏', '轻小说'] as GenreKey[], note: '节奏爽感与青春幻想' },
]

function createSeededRandom(seed: number) {
  let current = seed % 2147483647
  if (current <= 0) current += 2147483646
  return () => {
    current = (current * 16807) % 2147483647
    return (current - 1) / 2147483646
  }
}

function pick<T>(random: () => number, items: T[]): T {
  return items[Math.floor(random() * items.length)]
}

function randomInt(random: () => number, min: number, max: number) {
  return Math.floor(random() * (max - min + 1)) + min
}

function rotateColors(colors: [string, string, string], offset: number) {
  const values = [...colors]
  return [
    values[offset % 3],
    values[(offset + 1) % 3],
    values[(offset + 2) % 3],
  ] as [string, string, string]
}

function createCover(colors: [string, string, string], offset: number) {
  const [first, second, third] = rotateColors(colors, offset)
  return `linear-gradient(155deg, ${first} 0%, ${second} 55%, ${third} 100%)`
}

function createAuthor(random: () => number) {
  const surname = pick(random, authorSurnames)
  const given = `${pick(random, authorGivenFirst)}${pick(random, authorGivenSecond)}`
  const suffix = pick(random, authorTitleSuffix)
  return `${surname}${given}${suffix}`
}

function createTitle(random: () => number, genre: GenreKey) {
  const lexicon = genreLexicon[genre]
  const prefix = pick(random, lexicon.prefixes)
  const suffix = pick(random, lexicon.suffixes)
  switch (randomInt(random, 0, 3)) {
    case 0:
      return `${prefix}${suffix}`
    case 1:
      return `${prefix}之${suffix}`
    case 2:
      return `${prefix}${pick(random, ['纪事', '长夜', '回信', '简史', '狂潮', '手札'])}`
    default:
      return `${prefix}${pick(random, ['纪', '录', '书', '谣'])}`
  }
}

function createSummary(random: () => number, genre: GenreKey) {
  const lexicon = genreLexicon[genre]
  return `${pick(random, lexicon.roles)}在${pick(random, lexicon.scenes)}觉醒${pick(random, lexicon.powers)}，从此被卷入一场无法回头的命运布局。`
}

function createChapterTitle(random: () => number, genre: GenreKey) {
  const lexicon = genreLexicon[genre]
  return `第${randomInt(random, 8, 328)}章：${pick(random, lexicon.chapterFirst)}${pick(random, lexicon.chapterSecond)}`
}

function formatTime(index: number, minutesStep: number) {
  const time = new Date('2026-04-16T16:38:00+08:00')
  time.setMinutes(time.getMinutes() - index * minutesStep)
  const month = `${time.getMonth() + 1}`.padStart(2, '0')
  const day = `${time.getDate()}`.padStart(2, '0')
  const hours = `${time.getHours()}`.padStart(2, '0')
  const minutes = `${time.getMinutes()}`.padStart(2, '0')
  return `${month}-${day} ${hours}:${minutes}`
}

function uniqueById<T extends { id: string }>(items: T[]) {
  const seen = new Set<string>()
  return items.filter((item) => {
    if (seen.has(item.id)) return false
    seen.add(item.id)
    return true
  })
}

export function buildHomePageData(seed = 20260416): HomePageData {
  const random = createSeededRandom(seed)
  const books: HomeBook[] = []
  let bookCounter = 1

  for (const genre of genreDefinitions) {
    for (let index = 0; index < 9; index += 1) {
      const lexicon = genreLexicon[genre.key]
      const tags = [...lexicon.tags]
        .sort(() => random() - 0.5)
        .slice(0, 3)

      books.push({
        id: `book-${bookCounter}`,
        title: createTitle(random, genre.key),
        author: createAuthor(random),
        genre: genre.key,
        summary: createSummary(random, genre.key),
        hook: `${pick(random, hookPool)} · ${pick(random, lexicon.tags)}`,
        chapterTitle: createChapterTitle(random, genre.key),
        wordCount: randomInt(random, 18, 280) * 10000,
        heat: randomInt(random, 120000, 990000),
        recommend: randomInt(random, 8000, 160000),
        ticket: randomInt(random, 1200, 26000),
        score: randomInt(random, 78, 99),
        freshScore: randomInt(random, 70, 100),
        cover: createCover(genre.coverColors, index),
        accent: genre.accent,
        status: pick(random, statusPool),
        tags,
      })
      bookCounter += 1
    }
  }

  const byMetric = (metric: keyof Pick<HomeBook, 'ticket' | 'heat' | 'score' | 'recommend' | 'freshScore'>) =>
    [...books].sort((left, right) => Number(right[metric]) - Number(left[metric]))

  const heroGenres: GenreKey[] = ['玄幻', '都市', '科幻', '历史']
  const heroSlides = heroGenres.map((genreKey, index) => {
    const book = byMetric(index % 2 === 0 ? 'heat' : 'ticket').find((item) => item.genre === genreKey) || books[index]
    return {
      id: `hero-${genreKey}`,
      genre: genreKey,
      title: book.title,
      lead: `${genreKey}焦点`,
      summary: book.summary,
      chapterTitle: book.chapterTitle,
      tags: book.tags,
      stats: [
        { label: '热度', value: book.heat },
        { label: '月票', value: book.ticket },
        { label: '推荐', value: book.recommend },
      ],
      cover: book.cover,
      accent: book.accent,
    }
  })

  const hotSorted = byMetric('heat')
  const newSorted = byMetric('freshScore')
  const scoreSorted = byMetric('score')

  const promoCards: PromoCard[] = [
    {
      id: 'promo-hot',
      title: '本周高热推荐',
      caption: hotSorted[1].title,
      detail: `${hotSorted[1].summary.slice(0, 28)}……`,
      accent: hotSorted[1].accent,
      cover: hotSorted[1].cover,
      genre: hotSorted[1].genre,
    },
    {
      id: 'promo-new',
      title: '新书冲榜中',
      caption: newSorted[0].title,
      detail: `${newSorted[0].chapterTitle}，评论区正在持续升温。`,
      accent: newSorted[0].accent,
      cover: newSorted[0].cover,
      genre: newSorted[0].genre,
    },
    {
      id: 'promo-free',
      title: '今夜适合开读',
      caption: scoreSorted[2].title,
      detail: `${scoreSorted[2].hook}，适合一口气读到凌晨。`,
      accent: scoreSorted[2].accent,
      cover: scoreSorted[2].cover,
      genre: scoreSorted[2].genre,
    },
  ]

  const rankingBoards: RankingBoard[] = rankingDefinitions.map((definition) => ({
    id: definition.id,
    title: definition.title,
    subtitle: definition.subtitle,
    accent: definition.accent,
    books: byMetric(definition.metric).slice(0, 10),
  }))

  const shelves: GenreShelf[] = shelfDefinitions.map((definition) => ({
    id: definition.id,
    title: definition.title,
    glyph: definition.glyph,
    accent: definition.accent,
    note: definition.note,
    books: uniqueById(
      books
        .filter((book) => definition.genres.includes(book.genre))
        .sort((left, right) => right.score - left.score)
        .slice(0, 5),
    ),
  }))

  const updates: UpdateItem[] = hotSorted.slice(0, 16).map((book, index) => ({
    id: `update-${book.id}`,
    genre: book.genre,
    title: book.title,
    chapterTitle: book.chapterTitle,
    author: book.author,
    time: formatTime(index, randomInt(random, 5, 13)),
    badge: pick(random, updateBadges),
  }))

  const authorSpotlights: AuthorSpotlight[] = heroSlides.slice(0, 3).map((slide, index) => {
    const related = books.filter((book) => book.genre === slide.genre).slice(index, index + 4)
    const author = related[0]?.author || slide.title.slice(0, 2)
    return {
      id: `author-${index}`,
      name: author,
      title: `擅长 ${slide.genre} 题材的签约作者`,
      summary: `${author}常以层层推进的节奏书写${slide.genre}故事，代表作多以强钩子开篇和连续反转见长。`,
      works: related.map((book) => book.title).slice(0, 3),
      accent: slide.accent,
      initials: author.slice(0, 2),
    }
  })

  return {
    genres: genreDefinitions,
    allBooks: books,
    heroSlides,
    promoCards,
    hotSpotlight: hotSorted[0],
    hotBooks: hotSorted.slice(1, 7),
    rankingBoards,
    shelves,
    updates,
    authorSpotlights,
    newReleases: newSorted.slice(0, 8),
    freeReading: scoreSorted.slice(6, 12),
  }
}
