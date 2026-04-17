export type LibrarySource = 'api' | 'mock'

export interface LibraryBook {
  id: number
  title: string
  author: string
  coverUrl?: string
  category: string
  description: string
  wordCount: number
  recommendCount: number
  readCount: number
  status: string
  isFree: boolean
  updatedAt?: string | null
  chapterCount: number
  tags: string[]
  source: LibrarySource
}

export interface LibraryChapter {
  id: number
  bookId: number
  chapterNumber: number
  title: string
  wordCount: number
  preview: string
}

export interface LibraryChapterDetail extends LibraryChapter {
  content: string
  prevChapter: number | null
  nextChapter: number | null
}

type MockBlueprint = {
  id: number
  title: string
  author: string
  category: string
  description: string
  status: string
  isFree: boolean
  tags: string[]
  chapterTitles: string[]
}

const blueprints: MockBlueprint[] = [
  {
    id: 9001,
    title: '雾港回声',
    author: '沈星遥',
    category: '悬疑',
    description: '暴雨与海雾笼住旧港，记者许昼在一份失踪名单里看见了自己熟悉的名字。',
    status: '连载中',
    isFree: true,
    tags: ['悬疑', '旧案', '港口'],
    chapterTitles: ['雨夜来信', '码头回声', '停摆钟楼', '无人的证词', '灰仓门后', '第三条航道'],
  },
  {
    id: 9002,
    title: '天穹织火录',
    author: '顾临川',
    category: '玄幻',
    description: '熔城少年在废墟下唤醒天火纹章，命运从此不再允许他只是一个旁观者。',
    status: '连载中',
    isFree: true,
    tags: ['玄幻', '热血', '成长'],
    chapterTitles: ['炉火开纹', '古殿潮音', '焰骨试炼', '夜渡王庭', '碎星长桥', '山门鸣钟'],
  },
  {
    id: 9003,
    title: '零度航线',
    author: '林折光',
    category: '科幻',
    description: '一艘深空回收船捞起失效舱体，却发现舱内导航员来自三十年前的事故。',
    status: '已完结',
    isFree: false,
    tags: ['科幻', '深空', '时间误差'],
    chapterTitles: ['冷舱苏醒', '航标偏移', '寂静坐标', '镜像星图', '零度折返', '最终靠泊'],
  },
  {
    id: 9004,
    title: '长街见雪',
    author: '程不渡',
    category: '武侠',
    description: '灭门案后唯一活下来的少镖头，带着断刀和旧账，重新走回那条落雪的长街。',
    status: '连载中',
    isFree: true,
    tags: ['武侠', '复仇', '江湖'],
    chapterTitles: ['客栈灯寒', '断刀上路', '雪巷旧识', '桥边试锋', '雨中拜帖', '长街决意'],
  },
  {
    id: 9005,
    title: '云上春信',
    author: '纪南歌',
    category: '轻小说',
    description: '广播室里一卷写着未来日期的磁带，让普通校园日常多了一层会改变命运的回音。',
    status: '连载中',
    isFree: true,
    tags: ['校园', '轻小说', '青春'],
    chapterTitles: ['广播室的磁带', '被改写的值日表', '天台借风', '夏祭前夜', '误点发送', '春信抵达'],
  },
  {
    id: 9006,
    title: '长安夜行备忘录',
    author: '燕归迟',
    category: '历史',
    description: '连环火案搅动长安夜色，一名低阶史官在旧档残页中看见朝堂最想掩去的秘密。',
    status: '已完结',
    isFree: true,
    tags: ['历史', '朝堂', '探案'],
    chapterTitles: ['更鼓未尽', '旧档残页', '坊门熄灯', '宫墙夜火', '朱笔改句', '长安初雪'],
  },
  {
    id: 9007,
    title: '城市失焦面',
    author: '周闻笙',
    category: '都市',
    description: '镜头会提前捕捉失控瞬间的摄影师，在一次商业拍摄后意外卷进旧案风暴。',
    status: '连载中',
    isFree: false,
    tags: ['都市', '职业', '悬念'],
    chapterTitles: ['镜头偏差', '高架晚风', '空白底片', '深夜片场', '失焦来电', '重拍那一夜'],
  },
  {
    id: 9008,
    title: '扶风问月',
    author: '江照白',
    category: '仙侠',
    description: '外门弟子裴照在古祠中捡到一面会在月下说话的铜镜，旧劫因此开始复苏。',
    status: '连载中',
    isFree: true,
    tags: ['仙侠', '修行', '秘境'],
    chapterTitles: ['月下古镜', '山门薄雾', '祠中灵息', '夜半问剑', '旧劫残页', '照月归途'],
  },
]

const sceneMap: Record<string, string[]> = {
  悬疑: ['潮湿的旧码头', '只亮着半盏灯的值班室', '海雾弥漫的防波堤'],
  玄幻: ['翻涌热浪的熔城外环', '刻满旧纹的山门石阶', '被火光映红的试炼战台'],
  科幻: ['低温回收舱的蓝白冷光里', '漂浮碎屑掠过的舷窗边', '故障提示不断闪烁的导航室'],
  武侠: ['落雪压住脚印的长街口', '茶烟未散的驿路客栈', '刀光掠过又熄灭的暗巷里'],
  轻小说: ['午后无人的广播室', '被晚霞染成橘色的操场看台', '总会漏风的旧校舍走廊'],
  历史: ['更鼓刚过的坊门前', '堆满卷宗的值房里', '宫灯压得很低的偏殿长廊'],
  都市: ['玻璃幕墙映出霓虹的街角', '凌晨仍未收工的摄影棚', '高架桥下回声很重的空地'],
  仙侠: ['月色浸透的山门古阶', '灵气稀薄却格外安静的旧祠里', '钟声传得很远的后山道场'],
}

const feelingMap = ['不安', '笃定', '迟疑', '清醒', '克制', '警觉']
const turnMap = ['线索突然彼此咬合', '沉默已久的人终于开口', '看似平静的局面裂开了第一道缝', '所有人的注意力都被悄悄改写']
const endingMap = ['真正的转折还在下一页等着它自己露面。', '这一晚留下的余波，很快就会把每个人推向新的位置。', '答案没有完全出现，但方向已经无可回头。']

function hashValue(input: string) {
  let value = 0
  for (const char of input) {
    value = (value * 31 + char.charCodeAt(0)) % 1000000007
  }
  return value
}

function pickBySeed<T>(items: T[], seed: number, offset: number = 0) {
  return items[(seed + offset) % items.length]
}

function buildContent(book: MockBlueprint, chapterTitle: string, chapterNumber: number) {
  const seed = hashValue(`${book.title}-${chapterTitle}-${chapterNumber}`)
  const scene = pickBySeed(sceneMap[book.category] || sceneMap.都市, seed)
  const feeling = pickBySeed(feelingMap, seed, 3)
  const turn = pickBySeed(turnMap, seed, 5)
  const ending = pickBySeed(endingMap, seed, 7)

  return [
    `${scene}，第${chapterNumber}章《${chapterTitle}》缓缓拉开。${book.title}的故事在这里不急着制造巨响，而是先把空气压低，让人物的呼吸、动作和欲言又止的停顿都带上重量。`,
    `${book.description}这一层背景在本章里被重新照亮。主角并没有一次性得到答案，反而是在一件件小事里察觉到偏差：有人刻意回避目光，有人把话说到一半，有人明明站得很近，却像已经退到了故事之外。`,
    `这种推进带着${feeling}的质感。表面上每个人都还维持着秩序，可真正重要的信息正在边缘悄悄交换。等到${turn}时，读者才会意识到，前面所有细小的铺垫其实都在为这一刻抬高张力。`,
    `章节后半段把情绪重新收束到人物选择上。主角没有草率行动，而是记住了眼前的环境、对话和那句几乎被掩过去的话，因为他知道，下一次再面对同样的局，自己必须拿出更清晰也更锋利的回应。`,
    `尾声没有直接给出结果，而是让新的问题顺着情绪自然留下。${ending}`,
  ].join('\n\n')
}

const mockBooks = blueprints.map((book) => {
  const chapters = book.chapterTitles.map((chapterTitle, chapterIndex) => {
    const content = buildContent(book, chapterTitle, chapterIndex + 1)
    const id = book.id * 100 + chapterIndex + 1
    return {
      id,
      bookId: book.id,
      chapterNumber: chapterIndex + 1,
      title: `第${chapterIndex + 1}章 ${chapterTitle}`,
      preview: content.slice(0, 68).trim(),
      content,
      wordCount: content.length,
    }
  })

  return {
    ...book,
    chapters,
    wordCount: chapters.reduce((sum, chapter) => sum + chapter.wordCount, 0),
    recommendCount: 15000 + (book.id % 7) * 6800,
    readCount: 230000 + (book.id % 5) * 97000,
    updatedAt: `2026-04-${String(10 + (book.id % 8)).padStart(2, '0')}`,
  }
})

export function getMockBooks(): LibraryBook[] {
  return mockBooks.map((book) => ({
    id: book.id,
    title: book.title,
    author: book.author,
    coverUrl: '',
    category: book.category,
    description: book.description,
    wordCount: book.wordCount,
    recommendCount: book.recommendCount,
    readCount: book.readCount,
    status: book.status,
    isFree: book.isFree,
    updatedAt: book.updatedAt,
    chapterCount: book.chapters.length,
    tags: [...book.tags],
    source: 'mock',
  }))
}

export function getMockBookBundle(bookId: number) {
  const book = mockBooks.find((item) => item.id === bookId) ?? mockBooks[0]
  const chapters: LibraryChapter[] = book.chapters.map((chapter) => ({
    id: chapter.id,
    bookId: chapter.bookId,
    chapterNumber: chapter.chapterNumber,
    title: chapter.title,
    wordCount: chapter.wordCount,
    preview: chapter.preview,
  }))

  return {
    source: 'mock' as const,
    book: getMockBooks().find((item) => item.id === book.id)!,
    chapters,
  }
}

export function getMockReaderBundle(bookId: number, chapterNumber: number) {
  const bundle = getMockBookBundle(bookId)
  const chapter = bundle.chapters.find((item) => item.chapterNumber === chapterNumber) ?? bundle.chapters[0]
  const detailSource = mockBooks.find((item) => item.id === bundle.book.id)!
  const raw = detailSource.chapters.find((item) => item.chapterNumber === chapter.chapterNumber)!

  const chapterDetail: LibraryChapterDetail = {
    ...chapter,
    content: raw.content,
    prevChapter: chapter.chapterNumber > 1 ? chapter.chapterNumber - 1 : null,
    nextChapter: chapter.chapterNumber < bundle.chapters.length ? chapter.chapterNumber + 1 : null,
  }

  return {
    ...bundle,
    chapter: chapterDetail,
  }
}
