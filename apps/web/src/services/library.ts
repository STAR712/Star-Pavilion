import { getBookDetail, getBooks, getChapterContent, getChapters } from '@/api'
import {
  getMockBookBundle,
  getMockBooks,
  getMockReaderBundle,
  type LibraryBook,
  type LibraryChapter,
  type LibraryChapterDetail,
  type LibrarySource,
} from '@/data/mockLibrary'

export const categoryPaletteMap: Record<string, { accent: string; surface: string; glow: string }> = {
  玄幻: { accent: '#f97316', surface: 'linear-gradient(135deg, #2f1a10, #7c2d12 55%, #f59e0b)', glow: 'rgba(249, 115, 22, 0.22)' },
  仙侠: { accent: '#0f766e', surface: 'linear-gradient(135deg, #062b2d, #0f766e 50%, #7dd3fc)', glow: 'rgba(15, 118, 110, 0.2)' },
  科幻: { accent: '#2563eb', surface: 'linear-gradient(135deg, #081833, #1d4ed8 55%, #60a5fa)', glow: 'rgba(37, 99, 235, 0.2)' },
  武侠: { accent: '#b45309', surface: 'linear-gradient(135deg, #2f1208, #9a3412 52%, #fb923c)', glow: 'rgba(180, 83, 9, 0.22)' },
  悬疑: { accent: '#475569', surface: 'linear-gradient(135deg, #111827, #334155 55%, #94a3b8)', glow: 'rgba(71, 85, 105, 0.22)' },
  都市: { accent: '#db2777', surface: 'linear-gradient(135deg, #381021, #be185d 55%, #fb7185)', glow: 'rgba(219, 39, 119, 0.22)' },
  历史: { accent: '#a16207', surface: 'linear-gradient(135deg, #36210d, #a16207 55%, #facc15)', glow: 'rgba(161, 98, 7, 0.22)' },
  轻小说: { accent: '#ec4899', surface: 'linear-gradient(135deg, #4a1432, #db2777 55%, #f9a8d4)', glow: 'rgba(236, 72, 153, 0.2)' },
}

export function getCategoryPalette(category: string) {
  return categoryPaletteMap[category] ?? {
    accent: '#7c3aed',
    surface: 'linear-gradient(135deg, #312e81, #7c3aed 55%, #c4b5fd)',
    glow: 'rgba(124, 58, 237, 0.2)',
  }
}

function buildTags(category: string, status: string, isFree: boolean) {
  return [category, status, isFree ? '免费阅读' : '精选付费']
}

function mapApiBook(book: any): LibraryBook {
  return {
    id: Number(book.id),
    title: book.title,
    author: book.author,
    coverUrl: book.cover_url || '',
    category: book.category || '都市',
    description: book.description || '这本书暂时还没有补充简介，但故事已经开始向前滚动。',
    wordCount: Number(book.word_count || 0),
    recommendCount: Number(book.recommend_count || 0),
    readCount: Number(book.read_count || 0),
    status: book.status || '连载中',
    isFree: Boolean(book.is_free),
    updatedAt: book.updated_at || null,
    chapterCount: Number(book.chapter_count || 0),
    tags: buildTags(book.category || '都市', book.status || '连载中', Boolean(book.is_free)),
    source: 'api',
  }
}

function mapApiChapter(bookId: number, chapter: any): LibraryChapter {
  return {
    id: Number(chapter.id),
    bookId,
    chapterNumber: Number(chapter.chapter_number),
    title: chapter.title,
    wordCount: Number(chapter.word_count || 0),
    preview: `进入 ${chapter.title}，继续当前的叙事推进。`,
  }
}

function mapApiChapterDetail(bookId: number, chapter: any): LibraryChapterDetail {
  return {
    id: Number(chapter.id),
    bookId,
    chapterNumber: Number(chapter.chapter_number),
    title: chapter.title,
    wordCount: Number(chapter.word_count || 0),
    preview: String(chapter.content || '').slice(0, 68).trim(),
    content: chapter.content || '',
    prevChapter: chapter.prev_chapter ?? null,
    nextChapter: chapter.next_chapter ?? null,
  }
}

export async function fetchLibraryBooks(limit: number = 12): Promise<{ books: LibraryBook[]; source: LibrarySource }> {
  try {
    const { data } = await getBooks({ page: 1, size: Math.max(limit, 20) })
    const books = Array.isArray(data?.books) ? data.books.map(mapApiBook) : []
    if (books.length === 0) {
      throw new Error('empty_books')
    }
    return {
      books: books.slice(0, limit),
      source: 'api',
    }
  } catch {
    return {
      books: getMockBooks().slice(0, limit),
      source: 'mock',
    }
  }
}

export async function fetchBookBundle(bookId: number): Promise<{
  book: LibraryBook
  chapters: LibraryChapter[]
  source: LibrarySource
}> {
  try {
    const [bookRes, chaptersRes] = await Promise.all([getBookDetail(bookId), getChapters(bookId)])
    const chapters = Array.isArray(chaptersRes.data?.chapters)
      ? chaptersRes.data.chapters.map((chapter: any) => mapApiChapter(bookId, chapter))
      : []

    if (!bookRes.data || chapters.length === 0) {
      throw new Error('empty_book_bundle')
    }

    return {
      book: {
        ...mapApiBook(bookRes.data),
        chapterCount: chapters.length,
      },
      chapters,
      source: 'api',
    }
  } catch {
    return getMockBookBundle(bookId)
  }
}

export async function fetchReaderBundle(bookId: number, chapterNumber: number): Promise<{
  book: LibraryBook
  chapters: LibraryChapter[]
  chapter: LibraryChapterDetail
  source: LibrarySource
}> {
  try {
    const [bookRes, chaptersRes, chapterRes] = await Promise.all([
      getBookDetail(bookId),
      getChapters(bookId),
      getChapterContent(bookId, chapterNumber),
    ])

    const chapters = Array.isArray(chaptersRes.data?.chapters)
      ? chaptersRes.data.chapters.map((chapter: any) => mapApiChapter(bookId, chapter))
      : []

    if (!bookRes.data || !chapterRes.data || chapters.length === 0) {
      throw new Error('empty_reader_bundle')
    }

    return {
      book: {
        ...mapApiBook(bookRes.data),
        chapterCount: chapters.length,
      },
      chapters,
      chapter: mapApiChapterDetail(bookId, chapterRes.data),
      source: 'api',
    }
  } catch {
    return getMockReaderBundle(bookId, chapterNumber)
  }
}
