/** 用户角色 */
export type UserRole = 'reader' | 'author' | 'admin'

/** 用户信息 */
export interface UserInfo {
  id: number
  username: string
  role: UserRole
  created_at?: string
}

/** 聊天消息 */
export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

/** 会话摘要 */
export interface ConversationSummary {
  id: number
  name: string
  book_id: number | null
  chapter_id: number | null
  timestamp: string
}

/** 书架条目 */
export interface BookshelfEntry {
  id: number
  book_id: number
  book_title: string
  book_author: string
  book_category?: string
  book_description?: string
  current_chapter: number
  progress: number
}

/** API 通用响应 */
export interface ApiResponse<T = unknown> {
  data?: T
  detail?: string
  message?: string
}

/** 分页参数 */
export interface PaginationParams {
  page?: number
  size?: number
}

/** 分页响应 */
export interface PaginatedResponse<T> {
  total: number
  page: number
  size: number
  items: T[]
}
