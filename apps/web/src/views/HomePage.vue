<template>
  <div class="home-page min-h-screen text-[#2f211c]">
    <header class="sticky top-0 z-40 border-b border-white/10 bg-[rgba(27,24,27,0.9)] backdrop-blur-xl">
      <div class="page-shell px-4">
        <div class="hidden h-10 items-center justify-between text-[12px] text-white/55 lg:flex">
          <div class="flex items-center gap-5">
            <span>星亭书城首页重构</span>
            <span>门户式布局 / 杂志感排版 / 小说场景优先</span>
          </div>
          <div class="flex items-center gap-4">
            <button class="hover:text-white/80" @click="scrollToSection('hot-recommendations')">热门推荐</button>
            <button class="hover:text-white/80" @click="scrollToSection('ranking-section')">分类榜单</button>
            <button class="hover:text-white/80" @click="scrollToSection('recent-updates')">最近更新</button>
          </div>
        </div>

        <div class="flex min-h-[74px] items-center gap-4 py-3">
          <router-link to="/" class="flex shrink-0 items-center gap-3">
            <div class="brand-mark">星</div>
            <div>
              <p class="home-serif text-[30px] leading-none text-white">Star Pavilion</p>
              <p class="mt-1 text-[11px] tracking-[0.34em] text-white/45">FICTION PORTAL</p>
            </div>
          </router-link>

          <nav class="ml-4 hidden items-center gap-6 text-[15px] text-white/78 xl:flex">
            <button class="nav-link" :class="{ 'nav-link--active': selectedGenre === '全部' }" @click="selectGenre('全部')">
              首页
            </button>
            <button
              v-for="genre in pageData.genres.slice(0, 6)"
              :key="genre.key"
              class="nav-link"
              :class="{ 'nav-link--active': selectedGenre === genre.key }"
              @click="selectGenre(genre.key)"
            >
              {{ genre.key }}
            </button>
            <router-link to="/rank" class="nav-link">排行</router-link>
            <router-link to="/author" class="nav-link">作家专区</router-link>
          </nav>

          <div class="ml-auto flex items-center gap-3">
            <label class="relative hidden w-[320px] overflow-hidden rounded-full border border-white/10 bg-white/10 md:flex">
              <input
                v-model="searchInput"
                type="text"
                placeholder="搜索一本今夜想读的小说"
                class="h-11 w-full bg-transparent px-5 pr-14 text-sm text-white placeholder:text-white/45 focus:outline-none"
                @keyup.enter="applySearch"
              />
              <button class="absolute inset-y-0 right-0 grid w-12 place-items-center text-white/80" @click="applySearch">
                <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M21 21l-4.35-4.35m1.85-5.15a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </button>
            </label>

            <button class="header-pill hidden md:inline-flex" @click="scrollToSection('reading-desk')">我的书架</button>
            <router-link to="/rank" class="header-pill header-pill--accent">榜单</router-link>
            <router-link to="/author" class="header-pill hidden sm:inline-flex">投稿</router-link>
          </div>
        </div>
      </div>
    </header>

    <main class="pb-20">
      <section class="page-shell px-4 pt-6">
        <div class="home-ribbon">
          <div class="max-w-3xl">
            <p class="text-[12px] tracking-[0.38em] text-white/65">PORTAL HOMEPAGE REFRAME</p>
            <h1 class="home-serif mt-4 text-4xl leading-tight text-white md:text-5xl">
              书写星河，点亮一张更完整的小说首页
            </h1>
            <p class="mt-4 max-w-2xl text-sm leading-7 text-white/82 md:text-base">
              以参考图中的 Header、左侧分类、中央主视觉和榜单网格为基础骨架，
              首页被重构为更现代的书城门户。核心内容集中在热门推荐、分类榜单和最近更新，
              并用种子随机生成的小说标题与章节名填满每一个展示容器。
            </p>
            <div class="mt-6 flex flex-wrap gap-3">
              <button class="action-btn action-btn--light" @click="scrollToSection('hot-recommendations')">浏览热门推荐</button>
              <router-link to="/rank" class="action-btn action-btn--outline">查看排行榜</router-link>
            </div>
            <div class="mt-6 flex flex-wrap gap-3">
              <span class="filter-pill">{{ selectedGenre === '全部' ? '当前视图：全站风向' : `当前题材：${selectedGenre}` }}</span>
              <span v-if="activeKeyword" class="filter-pill">关键词：{{ activeKeyword }}</span>
              <button v-if="activeKeyword || selectedGenre !== '全部'" class="filter-pill filter-pill--action" @click="clearFilters">
                重置筛选
              </button>
            </div>
          </div>

          <div class="grid gap-3 sm:grid-cols-3 lg:grid-cols-1">
            <div v-for="stat in headlineStats" :key="stat.label" class="metric-card">
              <p class="text-[11px] tracking-[0.28em] text-white/58">{{ stat.label }}</p>
              <p class="mt-3 home-serif text-3xl text-white">{{ stat.value }}</p>
              <p class="mt-2 text-sm leading-6 text-white/72">{{ stat.note }}</p>
            </div>
          </div>
        </div>
      </section>

      <section id="hero-portal" class="page-shell px-4 pt-6">
        <div class="grid gap-6 xl:grid-cols-[280px_minmax(0,1fr)_320px]">
          <aside class="space-y-6">
            <div class="portal-panel p-5 reveal-card">
              <div class="flex items-center justify-between">
                <div>
                  <p class="section-kicker">分类入口</p>
                  <h2 class="home-serif mt-2 text-2xl text-[#251915]">作品分类</h2>
                </div>
                <span class="rounded-full border border-[#d9c1b2] px-3 py-1 text-[11px] text-[#9b6b52]">10 大题材</span>
              </div>

              <div class="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-1">
                <button
                  class="genre-entry"
                  :class="{ 'genre-entry--active': selectedGenre === '全部' }"
                  @click="selectGenre('全部')"
                >
                  <span class="genre-glyph genre-glyph--all">全</span>
                  <span class="min-w-0 flex-1 text-left">
                    <span class="block text-sm font-semibold text-[#2d211d]">全部作品</span>
                    <span class="mt-1 block text-xs text-[#8b7267]">回到全站视图</span>
                  </span>
                </button>

                <button
                  v-for="genre in pageData.genres"
                  :key="genre.key"
                  class="genre-entry"
                  :class="{ 'genre-entry--active': selectedGenre === genre.key }"
                  :style="{ '--genre-accent': genre.accent, '--genre-surface': genre.surface }"
                  @click="selectGenre(genre.key)"
                >
                  <span class="genre-glyph" :style="{ background: genre.surface, color: genre.accent }">{{ genre.glyph }}</span>
                  <span class="min-w-0 flex-1 text-left">
                    <span class="block text-sm font-semibold text-[#2d211d]">{{ genre.key }}</span>
                    <span class="mt-1 block text-xs text-[#8b7267]">{{ genre.description }}</span>
                  </span>
                  <span class="text-xs font-medium text-[#9b6b52]">{{ formatCompact(genre.count) }}</span>
                </button>
              </div>
            </div>

            <div class="portal-panel p-5 reveal-card" style="animation-delay: 120ms;">
              <p class="section-kicker">阅读导览</p>
              <h2 class="home-serif mt-2 text-2xl text-[#251915]">今日首页结构</h2>
              <div class="mt-5 space-y-4 text-sm leading-7 text-[#6d584d]">
                <p>左侧：题材分类与快速切换，代替原有单列推荐。</p>
                <p>中央：主视觉轮播 + 三张推广卡，承担首页第一屏的情绪与重点信息。</p>
                <p>右侧：最近更新与阅读桌面，让“追更”成为首屏即达的行为。</p>
              </div>
            </div>
          </aside>

          <div class="space-y-6">
            <article class="portal-panel hero-stage reveal-card" :style="{ '--hero-accent': activeHero.accent }">
              <div class="grid gap-6 lg:grid-cols-[minmax(0,1.15fr)_280px]">
                <div class="p-6 md:p-8">
                  <div class="flex flex-wrap items-center gap-3">
                    <span class="rounded-full border border-white/14 bg-white/8 px-3 py-1 text-[11px] tracking-[0.28em] text-white/70">
                      {{ activeHero.lead }}
                    </span>
                    <span class="rounded-full bg-white/12 px-3 py-1 text-xs text-white/82">{{ activeHero.genre }}</span>
                  </div>

                  <h2 class="home-serif mt-5 max-w-3xl text-4xl leading-tight text-white md:text-[3.4rem]">
                    {{ activeHero.title }}
                  </h2>
                  <p class="mt-4 max-w-2xl text-sm leading-7 text-white/76 md:text-base">
                    {{ activeHero.summary }}
                  </p>

                  <div class="mt-5 flex flex-wrap gap-2">
                    <span
                      v-for="tag in activeHero.tags"
                      :key="tag"
                      class="rounded-full border border-white/10 bg-white/10 px-3 py-1 text-xs text-white/82"
                    >
                      {{ tag }}
                    </span>
                  </div>

                  <div class="mt-6 grid gap-3 sm:grid-cols-3">
                    <div v-for="stat in activeHero.stats" :key="stat.label" class="hero-stat">
                      <span class="text-[11px] tracking-[0.28em] text-white/52">{{ stat.label }}</span>
                      <strong class="mt-2 block text-xl text-white">{{ formatCompact(stat.value) }}</strong>
                    </div>
                  </div>

                  <div class="mt-7 flex flex-wrap gap-3">
                    <button class="action-btn action-btn--dark" @click="scrollToSection('recent-updates')">查看追更动态</button>
                    <router-link to="/author" class="action-btn action-btn--soft">进入作家专区</router-link>
                  </div>
                </div>

                <div class="px-6 pb-6 lg:px-8 lg:py-8">
                  <div class="book-cover book-cover--hero" :style="{ background: activeHero.cover }">
                    <span class="book-cover__genre">{{ activeHero.genre }}</span>
                    <div class="book-cover__title">{{ activeHero.title }}</div>
                    <p class="book-cover__chapter">{{ activeHero.chapterTitle }}</p>
                  </div>

                  <div class="mt-4 grid gap-3">
                    <button
                      v-for="(slide, index) in pageData.heroSlides"
                      :key="slide.id"
                      class="hero-tab"
                      :class="{ 'hero-tab--active': index === activeHeroIndex }"
                      :style="index === activeHeroIndex ? { '--tab-accent': slide.accent } : undefined"
                      @click="setHero(index)"
                    >
                      <span class="text-left">
                        <span class="block text-xs tracking-[0.2em] text-white/52">{{ slide.genre }}</span>
                        <span class="mt-1 block truncate text-sm font-medium text-white">{{ slide.title }}</span>
                      </span>
                      <span class="text-xs text-white/42">{{ formatCompact(slide.stats[0].value) }}</span>
                    </button>
                  </div>
                </div>
              </div>
            </article>

            <div class="grid gap-4 md:grid-cols-3">
              <article
                v-for="(promo, index) in displayPromoCards"
                :key="promo.id"
                class="portal-panel p-5 reveal-card"
                :style="{ animationDelay: `${index * 80 + 120}ms` }"
              >
                <p class="section-kicker" :style="{ color: promo.accent }">{{ promo.title }}</p>
                <div class="mt-4 flex items-start gap-4">
                  <div class="mini-cover" :style="{ background: promo.cover }">
                    <span>{{ promo.genre }}</span>
                  </div>
                  <div class="min-w-0 flex-1">
                    <h3 class="home-serif text-2xl leading-tight text-[#251915]">{{ promo.caption }}</h3>
                    <p class="mt-3 text-sm leading-7 text-[#6d584d]">{{ promo.detail }}</p>
                  </div>
                </div>
              </article>
            </div>
          </div>

          <aside class="space-y-6">
            <div class="portal-panel p-5 reveal-card">
              <div class="flex items-center justify-between">
                <div>
                  <p class="section-kicker">即时动态</p>
                  <h2 class="home-serif mt-2 text-2xl text-[#251915]">最近更新</h2>
                </div>
                <button class="text-xs text-[#9b6b52] transition hover:text-[#7f3f2a]" @click="scrollToSection('recent-updates')">
                  展开更多
                </button>
              </div>

              <div class="mt-5 space-y-3">
                <article
                  v-for="update in displayUpdates.slice(0, 6)"
                  :key="update.id"
                  class="rounded-[20px] border border-[#efe0d4] bg-white/75 px-4 py-3 transition hover:-translate-y-0.5 hover:shadow-[0_14px_30px_rgba(86,57,40,0.08)]"
                >
                  <div class="flex items-center justify-between gap-3">
                    <span class="rounded-full px-2.5 py-1 text-[11px]" :style="{ background: getGenreMeta(update.genre).surface, color: getGenreMeta(update.genre).accent }">
                      {{ update.genre }}
                    </span>
                    <span class="text-[11px] text-[#b18b79]">{{ update.time }}</span>
                  </div>
                  <h3 class="mt-3 truncate text-sm font-semibold text-[#2d211d]">{{ update.title }}</h3>
                  <p class="mt-1 truncate text-xs text-[#7d665b]">{{ update.chapterTitle }}</p>
                </article>
              </div>
            </div>

            <div id="reading-desk" class="portal-panel p-5 reveal-card" style="animation-delay: 160ms;">
              <p class="section-kicker">阅读桌面</p>
              <h2 class="home-serif mt-2 text-2xl text-[#251915]">继续阅读</h2>

              <template v-if="readingEntry">
                <div class="mt-5 rounded-[24px] border border-[#efe0d4] bg-white/80 p-5">
                  <p class="text-xs tracking-[0.22em] text-[#aa7d67]">BOOKSHELF RESUME</p>
                  <h3 class="mt-3 home-serif text-2xl text-[#251915]">{{ readingEntry.book_title }}</h3>
                  <p class="mt-2 text-sm leading-7 text-[#6d584d]">
                    已读至第 {{ readingChapter }} 章，当前进度 {{ readingProgress }}%
                  </p>
                  <div class="mt-4 h-2 rounded-full bg-[#f0e0d2]">
                    <div class="h-full rounded-full bg-[linear-gradient(90deg,#b43b2d,#dd7a54)]" :style="{ width: `${readingProgress}%` }"></div>
                  </div>
                  <button class="mt-5 w-full rounded-full bg-[#24191b] px-4 py-3 text-sm font-medium text-white transition hover:bg-[#3c2625]" @click="continueReading">
                    回到阅读页
                  </button>
                </div>
              </template>

              <template v-else>
                <div class="mt-5 rounded-[24px] border border-[#efe0d4] bg-white/80 p-5">
                  <div class="book-cover h-[220px]" :style="{ background: deskFallback.cover }">
                    <span class="book-cover__genre">{{ deskFallback.genre }}</span>
                    <div class="book-cover__title">{{ deskFallback.title }}</div>
                    <p class="book-cover__chapter">{{ deskFallback.chapterTitle }}</p>
                  </div>
                  <p class="mt-4 text-sm leading-7 text-[#6d584d]">
                    书架里还没有可续读的内容，先从这本高分新作开始，把首页第一屏也变成你的阅读入口。
                  </p>
                  <button class="mt-4 w-full rounded-full border border-[#d7c0b1] px-4 py-3 text-sm font-medium text-[#6b3c2f] transition hover:border-[#b43b2d] hover:text-[#b43b2d]" @click="scrollToSection('new-arrivals')">
                    去看新书推荐
                  </button>
                </div>
              </template>
            </div>
          </aside>
        </div>
      </section>

      <section id="hot-recommendations" class="page-shell px-4 pt-12">
        <div class="section-heading">
          <div>
            <p class="section-kicker">热门推荐</p>
            <h2 class="home-serif mt-2 text-4xl text-[#251915]">此刻最值得点开的故事</h2>
            <p class="mt-3 text-sm leading-7 text-[#786358]">
              {{ activeKeyword ? `已结合关键词“${activeKeyword}”进行优先展示，并自动补齐高热内容。` : '优先展示高热作品，同时遵循当前分类筛选。' }}
            </p>
          </div>
          <button class="section-link" @click="scrollToSection('ranking-section')">转到分类榜单</button>
        </div>

        <div class="mt-6 grid gap-6 xl:grid-cols-[1.18fr_1fr_1fr]">
          <article class="portal-panel p-6 reveal-card xl:row-span-2">
            <div class="flex flex-wrap items-center gap-3">
              <span class="rounded-full px-3 py-1 text-[11px]" :style="{ background: getGenreMeta(hotSpotlight.genre).surface, color: getGenreMeta(hotSpotlight.genre).accent }">
                {{ hotSpotlight.genre }}
              </span>
              <span class="rounded-full border border-[#e7d6ca] px-3 py-1 text-[11px] text-[#9b6b52]">{{ hotSpotlight.hook }}</span>
            </div>

            <div class="mt-6 grid gap-6 md:grid-cols-[220px_minmax(0,1fr)]">
              <div class="book-cover h-[320px]" :style="{ background: hotSpotlight.cover }">
                <span class="book-cover__genre">{{ hotSpotlight.genre }}</span>
                <div class="book-cover__title">{{ hotSpotlight.title }}</div>
                <p class="book-cover__chapter">{{ hotSpotlight.chapterTitle }}</p>
              </div>

              <div>
                <h3 class="home-serif text-4xl leading-tight text-[#251915]">{{ hotSpotlight.title }}</h3>
                <p class="mt-4 text-sm leading-8 text-[#6d584d]">{{ hotSpotlight.summary }}</p>

                <div class="mt-5 flex flex-wrap gap-2">
                  <span v-for="tag in hotSpotlight.tags" :key="tag" class="tag-chip">{{ tag }}</span>
                </div>

                <div class="mt-6 grid gap-3 sm:grid-cols-3">
                  <div class="stat-block">
                    <span>热度</span>
                    <strong>{{ formatCompact(hotSpotlight.heat) }}</strong>
                  </div>
                  <div class="stat-block">
                    <span>字数</span>
                    <strong>{{ formatWordCount(hotSpotlight.wordCount) }}</strong>
                  </div>
                  <div class="stat-block">
                    <span>月票</span>
                    <strong>{{ formatCompact(hotSpotlight.ticket) }}</strong>
                  </div>
                </div>
              </div>
            </div>
          </article>

          <article
            v-for="(book, index) in hotGrid"
            :key="book.id"
            class="portal-panel p-5 reveal-card"
            :style="{ animationDelay: `${index * 80 + 120}ms` }"
          >
            <div class="flex items-start gap-4">
              <div class="mini-cover mini-cover--tall" :style="{ background: book.cover }">
                <span>{{ book.genre }}</span>
              </div>
              <div class="min-w-0 flex-1">
                <div class="flex items-center justify-between gap-3">
                  <span class="rounded-full px-2.5 py-1 text-[11px]" :style="{ background: getGenreMeta(book.genre).surface, color: getGenreMeta(book.genre).accent }">
                    {{ book.genre }}
                  </span>
                  <span class="text-[11px] text-[#9b6b52]">{{ formatCompact(book.heat) }}</span>
                </div>
                <h3 class="mt-4 truncate text-lg font-semibold text-[#251915]">{{ book.title }}</h3>
                <p class="mt-2 text-sm text-[#9b6b52]">{{ book.author }}</p>
                <p class="mt-3 line-clamp-3 text-sm leading-7 text-[#6d584d]">{{ book.summary }}</p>
                <p class="mt-4 truncate text-xs text-[#8a6c60]">{{ book.chapterTitle }}</p>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section id="ranking-section" class="page-shell px-4 pt-12">
        <div class="section-heading">
          <div>
            <p class="section-kicker">分类榜单</p>
            <h2 class="home-serif mt-2 text-4xl text-[#251915]">五组榜单，快速扫过全站风向</h2>
            <p class="mt-3 text-sm leading-7 text-[#786358]">布局参考了传统书城门户的纵向榜单列，但在卡片细节和留白节奏上做了更现代的处理。</p>
          </div>
          <router-link to="/rank" class="section-link">进入完整排行页</router-link>
        </div>

        <div class="mt-6 grid gap-5 md:grid-cols-2 xl:grid-cols-5">
          <article
            v-for="(board, boardIndex) in pageData.rankingBoards"
            :key="board.id"
            class="portal-panel p-5 reveal-card"
            :style="{ animationDelay: `${boardIndex * 70}ms` }"
          >
            <div class="flex items-start justify-between gap-4">
              <div>
                <h3 class="home-serif text-3xl text-[#251915]">{{ board.title }}</h3>
                <p class="mt-2 text-xs tracking-[0.24em] text-[#9b6b52]">{{ board.subtitle }}</p>
              </div>
              <span class="rounded-full px-3 py-1 text-[11px]" :style="{ background: `${board.accent}12`, color: board.accent }">TOP 10</span>
            </div>

            <div class="mt-5 flex gap-4 rounded-[22px] border border-[#efe0d4] bg-white/78 p-4">
              <div class="mini-cover mini-cover--rank" :style="{ background: board.books[0].cover }">
                <span>{{ board.books[0].genre }}</span>
              </div>
              <div class="min-w-0 flex-1">
                <p class="text-[13px] font-semibold" :style="{ color: board.accent }">NO.1</p>
                <h4 class="mt-2 line-clamp-2 text-lg font-semibold leading-7 text-[#251915]">{{ board.books[0].title }}</h4>
                <p class="mt-2 text-sm text-[#8a6c60]">{{ board.books[0].author }}</p>
                <p class="mt-3 text-sm font-medium" :style="{ color: board.accent }">{{ boardMetric(board, board.books[0]) }}</p>
              </div>
            </div>

            <ol class="mt-5 space-y-3">
              <li
                v-for="(book, index) in board.books.slice(1)"
                :key="book.id"
                class="flex items-center gap-3 border-b border-[#f2e6dc] pb-3 last:border-b-0 last:pb-0"
              >
                <span class="rank-number" :style="rankNumberStyle(index, board.accent)">{{ index + 2 }}</span>
                <div class="min-w-0 flex-1">
                  <p class="truncate text-sm text-[#2d211d]">{{ book.title }}</p>
                </div>
                <span class="text-xs text-[#b09181]">{{ boardMetric(board, book) }}</span>
              </li>
            </ol>
          </article>
        </div>
      </section>

      <section class="page-shell px-4 pt-12">
        <div class="section-heading">
          <div>
            <p class="section-kicker">分类矩阵</p>
            <h2 class="home-serif mt-2 text-4xl text-[#251915]">热门作品与题材书单并排呈现</h2>
            <p class="mt-3 text-sm leading-7 text-[#786358]">这一段延续参考图中“左侧大推荐 + 右侧类别流”的结构，只保留最适合首页的内容密度。</p>
          </div>
          <button class="section-link" @click="scrollToSection('new-arrivals')">跳到新书推荐</button>
        </div>

        <div class="mt-6 grid gap-6 xl:grid-cols-[300px_minmax(0,1fr)]">
          <article class="portal-panel p-6 reveal-card">
            <p class="section-kicker">焦点作品</p>
            <div class="mt-5 book-cover h-[340px]" :style="{ background: pageData.hotSpotlight.cover }">
              <span class="book-cover__genre">{{ pageData.hotSpotlight.genre }}</span>
              <div class="book-cover__title">{{ pageData.hotSpotlight.title }}</div>
              <p class="book-cover__chapter">{{ pageData.hotSpotlight.chapterTitle }}</p>
            </div>
            <h3 class="home-serif mt-5 text-3xl text-[#251915]">{{ pageData.hotSpotlight.title }}</h3>
            <p class="mt-3 text-sm leading-8 text-[#6d584d]">{{ pageData.hotSpotlight.summary }}</p>
            <div class="mt-5 grid gap-3">
              <div class="stat-block">
                <span>推荐</span>
                <strong>{{ formatCompact(pageData.hotSpotlight.recommend) }}</strong>
              </div>
              <div class="stat-block">
                <span>状态</span>
                <strong>{{ pageData.hotSpotlight.status }}</strong>
              </div>
            </div>
          </article>

          <div class="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
            <article
              v-for="(shelf, index) in displayShelves"
              :key="shelf.id"
              class="portal-panel p-5 reveal-card"
              :style="{ animationDelay: `${index * 80}ms` }"
            >
              <div class="flex items-start justify-between gap-4">
                <div>
                  <h3 class="home-serif text-3xl text-[#251915]">{{ shelf.title }}</h3>
                  <p class="mt-2 text-sm leading-7 text-[#876c61]">{{ shelf.note }}</p>
                </div>
                <span class="shelf-glyph" :style="{ background: `${shelf.accent}12`, color: shelf.accent }">{{ shelf.glyph }}</span>
              </div>

              <ul class="mt-5 space-y-3">
                <li
                  v-for="book in shelf.books"
                  :key="book.id"
                  class="rounded-[18px] border border-[#efe0d4] bg-white/76 px-4 py-3"
                >
                  <p class="truncate text-sm font-semibold text-[#2d211d]">{{ book.title }}</p>
                  <p class="mt-1 truncate text-xs text-[#8a6c60]">{{ book.summary }}</p>
                </li>
              </ul>
            </article>
          </div>
        </div>
      </section>

      <section id="recent-updates" class="page-shell px-4 pt-12">
        <div class="section-heading">
          <div>
            <p class="section-kicker">最近更新</p>
            <h2 class="home-serif mt-2 text-4xl text-[#251915]">追更信息流与作者看板</h2>
            <p class="mt-3 text-sm leading-7 text-[#786358]">章节名使用语义化随机组合，例如“第 87 章：焚天试炼”“第 34 章：签字回线”，既有小说味，也能稳定撑满内容区。</p>
          </div>
          <button class="section-link" @click="scrollToSection('hero-portal')">回到首屏</button>
        </div>

        <div class="mt-6 grid gap-6 xl:grid-cols-[250px_minmax(0,1fr)_280px]">
          <div class="space-y-6">
            <article
              v-for="(book, index) in displayFreeReading"
              :key="book.id"
              class="portal-panel p-5 reveal-card"
              :style="{ animationDelay: `${index * 90}ms` }"
            >
              <p class="section-kicker">精选卡片</p>
              <div class="mt-4 book-cover h-[240px]" :style="{ background: book.cover }">
                <span class="book-cover__genre">{{ book.genre }}</span>
                <div class="book-cover__title">{{ book.title }}</div>
                <p class="book-cover__chapter">{{ book.chapterTitle }}</p>
              </div>
              <p class="mt-4 text-sm leading-7 text-[#6d584d]">{{ book.summary }}</p>
            </article>
          </div>

          <article class="portal-panel overflow-hidden p-0 reveal-card">
            <div class="hidden grid-cols-[86px_minmax(0,1.5fr)_1.2fr_0.9fr_90px] gap-3 border-b border-[#efe0d4] bg-[#faf2ea] px-6 py-4 text-[11px] tracking-[0.24em] text-[#9b6b52] md:grid">
              <span>分类</span>
              <span>作品名称</span>
              <span>最新章节</span>
              <span>作者</span>
              <span class="text-right">时间</span>
            </div>

            <div>
              <div
                v-for="update in displayUpdates"
                :key="update.id"
                class="border-b border-[#f2e6dc] px-5 py-4 last:border-b-0"
              >
                <div class="grid gap-2 md:grid-cols-[86px_minmax(0,1.5fr)_1.2fr_0.9fr_90px] md:items-center md:gap-3">
                  <div>
                    <span class="rounded-full px-2.5 py-1 text-[11px]" :style="{ background: getGenreMeta(update.genre).surface, color: getGenreMeta(update.genre).accent }">
                      {{ update.genre }}
                    </span>
                  </div>
                  <p class="truncate text-sm font-semibold text-[#2d211d]">{{ update.title }}</p>
                  <p class="truncate text-sm text-[#725d53]">{{ update.chapterTitle }}</p>
                  <div class="flex items-center gap-2 text-sm text-[#8a6c60]">
                    <span>{{ update.author }}</span>
                    <span class="hidden rounded-full border border-[#e7d6ca] px-2 py-0.5 text-[11px] text-[#b07e67] md:inline-flex">{{ update.badge }}</span>
                  </div>
                  <p class="text-right text-xs text-[#b09181]">{{ update.time }}</p>
                </div>
              </div>
            </div>
          </article>

          <div class="space-y-6">
            <article
              v-for="(author, index) in pageData.authorSpotlights"
              :key="author.id"
              class="portal-panel p-5 reveal-card"
              :style="{ animationDelay: `${index * 90}ms` }"
            >
              <div class="flex items-start gap-4">
                <div class="author-avatar" :style="{ background: `linear-gradient(145deg, ${author.accent}, #f4d7c9)` }">
                  {{ author.initials }}
                </div>
                <div class="min-w-0 flex-1">
                  <h3 class="home-serif text-2xl text-[#251915]">{{ author.name }}</h3>
                  <p class="mt-2 text-sm text-[#8a6c60]">{{ author.title }}</p>
                </div>
              </div>
              <p class="mt-4 text-sm leading-7 text-[#6d584d]">{{ author.summary }}</p>
              <div class="mt-4 space-y-2">
                <p v-for="work in author.works" :key="work" class="truncate text-sm text-[#2d211d]">{{ work }}</p>
              </div>
            </article>
          </div>
        </div>
      </section>

      <section id="new-arrivals" class="page-shell px-4 pt-12">
        <div class="section-heading">
          <div>
            <p class="section-kicker">新书推荐</p>
            <h2 class="home-serif mt-2 text-4xl text-[#251915]">持续铺满底部的书封卡片流</h2>
            <p class="mt-3 text-sm leading-7 text-[#786358]">底部使用响应式卡片阵列，延续参考图里“成排书封”的视觉记忆，但改为更轻盈的卡面和更清晰的排版节奏。</p>
          </div>
          <button class="section-link" @click="scrollToSection('hero-portal')">返回顶部内容</button>
        </div>

        <div class="mt-6 grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
          <article
            v-for="(book, index) in displayNewReleases"
            :key="book.id"
            class="portal-panel p-5 reveal-card"
            :style="{ animationDelay: `${index * 60}ms` }"
          >
            <div class="flex gap-4">
              <div class="mini-cover mini-cover--new" :style="{ background: book.cover }">
                <span>{{ book.genre }}</span>
              </div>
              <div class="min-w-0 flex-1">
                <div class="flex items-center justify-between gap-3">
                  <span class="rounded-full px-2.5 py-1 text-[11px]" :style="{ background: getGenreMeta(book.genre).surface, color: getGenreMeta(book.genre).accent }">
                    {{ book.genre }}
                  </span>
                  <span class="text-xs text-[#b09181]">{{ formatWordCount(book.wordCount) }}</span>
                </div>
                <h3 class="mt-4 line-clamp-2 text-lg font-semibold leading-7 text-[#251915]">{{ book.title }}</h3>
                <p class="mt-2 text-sm text-[#8a6c60]">{{ book.author }}</p>
                <p class="mt-3 line-clamp-3 text-sm leading-7 text-[#6d584d]">{{ book.summary }}</p>
                <div class="mt-4 flex flex-wrap gap-2">
                  <span v-for="tag in book.tags" :key="tag" class="tag-chip">{{ tag }}</span>
                </div>
              </div>
            </div>
          </article>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { buildHomePageData, type GenreKey, type GenreMeta, type HomeBook, type PromoCard, type RankingBoard, type UpdateItem } from '@/data/homePage'
import { useBookshelfStore } from '@/stores/bookshelf'

const router = useRouter()
const bookshelfStore = useBookshelfStore()
const pageData = buildHomePageData()

const searchInput = ref('')
const activeKeyword = ref('')
const selectedGenre = ref<GenreKey | '全部'>('全部')
const activeHeroIndex = ref(0)

const genreMap = new Map<GenreKey, GenreMeta>(pageData.genres.map((genre) => [genre.key, genre]))

function getGenreMeta(genre: GenreKey) {
  return genreMap.get(genre)!
}

function matchesKeyword(book: HomeBook) {
  const keyword = activeKeyword.value.trim()
  if (!keyword) return true
  return [book.title, book.author, book.summary, book.chapterTitle, book.tags.join(' ')].some((field) =>
    field.toLowerCase().includes(keyword.toLowerCase()),
  )
}

function updateMatchesKeyword(item: UpdateItem) {
  const keyword = activeKeyword.value.trim()
  if (!keyword) return true
  return [item.title, item.author, item.chapterTitle, item.genre].some((field) =>
    field.toLowerCase().includes(keyword.toLowerCase()),
  )
}

function matchesGenre<T extends { genre: GenreKey }>(item: T) {
  return selectedGenre.value === '全部' || item.genre === selectedGenre.value
}

function fillWithFallback<T extends { id: string }>(primary: T[], fallback: T[], size: number) {
  const next: T[] = []
  const seen = new Set<string>()

  for (const item of [...primary, ...fallback]) {
    if (seen.has(item.id)) continue
    next.push(item)
    seen.add(item.id)
    if (next.length === size) break
  }

  return next
}

function filterBooks(source: HomeBook[]) {
  return source.filter((book) => matchesGenre(book) && matchesKeyword(book))
}

function selectGenre(genre: GenreKey | '全部') {
  selectedGenre.value = genre
  if (genre !== '全部') {
    const heroIndex = pageData.heroSlides.findIndex((slide) => slide.genre === genre)
    if (heroIndex >= 0) {
      activeHeroIndex.value = heroIndex
    }
  }
}

function setHero(index: number) {
  activeHeroIndex.value = index
  selectedGenre.value = pageData.heroSlides[index].genre
}

function scrollToSection(id: string) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function applySearch() {
  activeKeyword.value = searchInput.value.trim()
  scrollToSection('hot-recommendations')
}

function clearFilters() {
  searchInput.value = ''
  activeKeyword.value = ''
  selectedGenre.value = '全部'
  activeHeroIndex.value = 0
}

function continueReading() {
  if (!readingEntry.value) {
    scrollToSection('new-arrivals')
    return
  }

  router.push(`/read/${readingEntry.value.book_id}/${readingChapter.value}`)
}

function formatCompact(value: number) {
  if (value >= 100000000) return `${(value / 100000000).toFixed(1)}亿`
  if (value >= 10000) return `${(value / 10000).toFixed(value >= 100000 ? 0 : 1)}万`
  return value.toLocaleString('zh-CN')
}

function formatWordCount(value: number) {
  if (value >= 10000) return `${(value / 10000).toFixed(value >= 100000 ? 0 : 1)}万字`
  return `${value}字`
}

function boardMetric(board: RankingBoard, book: HomeBook) {
  switch (board.id) {
    case 'tickets':
      return `${formatCompact(book.ticket)} 月票`
    case 'hot':
      return `${formatCompact(book.heat)} 热度`
    case 'score':
      return `口碑 ${book.score}`
    case 'read':
      return `${formatCompact(book.recommend)} 推荐`
    default:
      return `新书指数 ${book.freshScore}`
  }
}

function rankNumberStyle(index: number, accent: string) {
  if (index < 2) {
    return {
      background: `${accent}16`,
      color: accent,
      borderColor: `${accent}22`,
    }
  }

  return {
    background: 'rgba(108, 87, 75, 0.08)',
    color: '#8d7469',
    borderColor: 'rgba(108, 87, 75, 0.12)',
  }
}

const activeHero = computed(() => pageData.heroSlides[activeHeroIndex.value] ?? pageData.heroSlides[0])

const headlineStats = computed(() => [
  {
    label: '全站热读',
    value: formatCompact(pageData.allBooks.reduce((sum, book) => sum + book.heat, 0)),
    note: '首屏内容采用门户式分栏，热度指标统一收敛到首页核心模块。',
  },
  {
    label: '题材矩阵',
    value: `${pageData.genres.length} 大类`,
    note: '左侧分类支持即时切换，热门推荐和更新流会跟随筛选变化。',
  },
  {
    label: '章节占位',
    value: `${pageData.updates.length} 条`,
    note: '章节名基于种子随机生成，语义统一且能稳定填满所有卡面。',
  },
])

const displayPromoCards = computed(() =>
  fillWithFallback(
    pageData.promoCards.filter((card) => matchesGenre(card as PromoCard) && (!activeKeyword.value || card.caption.includes(activeKeyword.value))),
    pageData.promoCards,
    3,
  ),
)

const hotSpotlight = computed(() => fillWithFallback(filterBooks([pageData.hotSpotlight, ...pageData.allBooks]), pageData.allBooks, 1)[0])

const hotGrid = computed(() => fillWithFallback(filterBooks(pageData.hotBooks), pageData.hotBooks, 4))

const displayShelves = computed(() => {
  const primary = selectedGenre.value === '全部'
    ? pageData.shelves
    : pageData.shelves.filter((shelf) => shelf.books.some((book) => book.genre === selectedGenre.value))
  return fillWithFallback(primary, pageData.shelves, 5)
})

const displayUpdates = computed(() =>
  fillWithFallback(
    pageData.updates.filter((item) => matchesGenre(item) && updateMatchesKeyword(item)),
    pageData.updates,
    12,
  ),
)

const displayNewReleases = computed(() => fillWithFallback(filterBooks(pageData.newReleases), pageData.newReleases, 8))

const displayFreeReading = computed(() => fillWithFallback(filterBooks(pageData.freeReading), pageData.freeReading, 2))

const readingEntry = computed(() =>
  bookshelfStore.books.find((item: any) => (item.progress ?? 0) < 100) || bookshelfStore.books[0] || null,
)

const readingProgress = computed(() => Math.max(0, Math.min(100, Math.round(readingEntry.value?.progress ?? 0))))

const readingChapter = computed(() => Math.max(1, Number(readingEntry.value?.current_chapter ?? 1)))

const deskFallback = computed(() => hotSpotlight.value)

onMounted(() => {
  bookshelfStore.fetchBookshelf().catch(() => undefined)
})
</script>

<style scoped>
.home-page {
  background:
    radial-gradient(circle at top left, rgba(255, 206, 157, 0.28), transparent 28%),
    radial-gradient(circle at top right, rgba(221, 102, 73, 0.16), transparent 22%),
    linear-gradient(180deg, #fcf8f2 0%, #f6efe5 46%, #f5ede1 100%);
}

.page-shell {
  max-width: 1440px;
  margin: 0 auto;
}

.home-serif {
  font-family: 'Iowan Old Style', 'Baskerville', 'Songti SC', 'STSong', serif;
}

.brand-mark {
  display: grid;
  height: 52px;
  width: 52px;
  place-items: center;
  border-radius: 18px;
  background:
    linear-gradient(145deg, rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0.06)),
    linear-gradient(135deg, #bb4b34, #7f2318);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.24);
  color: #fff;
  font-family: 'Iowan Old Style', 'Songti SC', serif;
  font-size: 26px;
  font-weight: 600;
}

.nav-link {
  position: relative;
  transition: color 0.2s ease;
}

.nav-link:hover,
.nav-link--active {
  color: #fff;
}

.nav-link--active::after {
  content: '';
  position: absolute;
  right: 0;
  bottom: -10px;
  left: 0;
  height: 2px;
  border-radius: 999px;
  background: linear-gradient(90deg, #d87c53, #f4c08b);
}

.header-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 84px;
  height: 42px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.82);
  font-size: 14px;
  transition: all 0.2s ease;
}

.header-pill:hover {
  border-color: rgba(255, 255, 255, 0.24);
  color: #fff;
}

.header-pill--accent {
  border-color: rgba(222, 120, 82, 0.4);
  background: linear-gradient(135deg, rgba(197, 70, 44, 0.95), rgba(228, 142, 95, 0.9));
  color: #fff;
}

.home-ribbon {
  display: grid;
  gap: 24px;
  border-radius: 32px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background:
    radial-gradient(circle at 88% 10%, rgba(255, 255, 255, 0.16), transparent 18%),
    radial-gradient(circle at 80% 80%, rgba(255, 203, 155, 0.16), transparent 22%),
    linear-gradient(135deg, #7c2117 0%, #bc4a2c 42%, #e2a05e 100%);
  padding: 32px;
  box-shadow: 0 30px 70px rgba(78, 26, 17, 0.18);
}

@media (min-width: 1024px) {
  .home-ribbon {
    grid-template-columns: minmax(0, 1.5fr) 320px;
  }
}

.metric-card {
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.08);
  padding: 18px 18px 20px;
}

.filter-pill {
  display: inline-flex;
  align-items: center;
  min-height: 38px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.08);
  padding: 0 14px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.82);
}

.filter-pill--action {
  cursor: pointer;
  transition: background 0.2s ease;
}

.filter-pill--action:hover {
  background: rgba(255, 255, 255, 0.14);
}

.portal-panel {
  position: relative;
  overflow: hidden;
  border-radius: 28px;
  border: 1px solid rgba(138, 104, 87, 0.12);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(255, 250, 245, 0.88));
  box-shadow: 0 20px 55px rgba(74, 44, 30, 0.08);
}

.portal-panel::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.26), transparent 28%);
  pointer-events: none;
}

.section-kicker {
  font-size: 11px;
  letter-spacing: 0.28em;
  text-transform: uppercase;
  color: #ab7f69;
}

.section-heading {
  display: flex;
  flex-wrap: wrap;
  align-items: end;
  justify-content: space-between;
  gap: 16px;
}

.section-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #8d5540;
  font-size: 14px;
  transition: color 0.2s ease;
}

.section-link:hover {
  color: #b43b2d;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 46px;
  padding: 0 18px;
  border-radius: 999px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.action-btn--light {
  background: #fff;
  color: #6c2d20;
}

.action-btn--outline {
  border: 1px solid rgba(255, 255, 255, 0.22);
  color: #fff;
}

.action-btn--dark {
  background: rgba(26, 17, 19, 0.82);
  color: #fff;
}

.action-btn--soft {
  border: 1px solid rgba(255, 255, 255, 0.18);
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}

.action-btn:hover {
  transform: translateY(-1px);
}

.genre-entry {
  display: flex;
  align-items: center;
  gap: 14px;
  border-radius: 22px;
  border: 1px solid rgba(148, 112, 94, 0.12);
  background: rgba(255, 255, 255, 0.72);
  padding: 14px 16px;
  transition: all 0.2s ease;
}

.genre-entry:hover,
.genre-entry--active {
  border-color: rgba(180, 59, 45, 0.22);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(255, 247, 242, 0.94));
  transform: translateY(-1px);
}

.genre-glyph {
  display: grid;
  height: 42px;
  width: 42px;
  place-items: center;
  border-radius: 14px;
  font-size: 18px;
  font-weight: 600;
}

.genre-glyph--all {
  background: linear-gradient(145deg, rgba(180, 59, 45, 0.1), rgba(255, 255, 255, 0.96));
  color: #b43b2d;
}

.hero-stage {
  background:
    radial-gradient(circle at top right, rgba(255, 255, 255, 0.16), transparent 18%),
    radial-gradient(circle at bottom left, rgba(255, 195, 145, 0.12), transparent 30%),
    linear-gradient(135deg, #23191b 0%, #5a2f28 52%, #9d543d 100%);
}

.hero-stat {
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.08);
  padding: 14px 16px;
}

.book-cover {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  overflow: hidden;
  border-radius: 26px;
  padding: 20px;
  color: #fff;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.16);
}

.book-cover::before {
  content: '';
  position: absolute;
  inset: 12px;
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  pointer-events: none;
}

.book-cover::after {
  content: '';
  position: absolute;
  inset: auto -15% 10% auto;
  height: 120px;
  width: 120px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.16);
  filter: blur(2px);
}

.book-cover--hero {
  min-height: 360px;
}

.book-cover__genre {
  position: relative;
  z-index: 1;
  align-self: flex-start;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.16);
  background: rgba(255, 255, 255, 0.09);
  padding: 6px 12px;
  font-size: 11px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
}

.book-cover__title {
  position: relative;
  z-index: 1;
  font-family: 'Iowan Old Style', 'Baskerville', 'Songti SC', serif;
  font-size: 2rem;
  line-height: 1.2;
  white-space: pre-line;
}

.book-cover__chapter {
  position: relative;
  z-index: 1;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.78);
}

.mini-cover {
  position: relative;
  display: flex;
  width: 88px;
  min-width: 88px;
  justify-content: end;
  overflow: hidden;
  border-radius: 20px;
  padding: 14px 12px;
  color: rgba(255, 255, 255, 0.78);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.15);
}

.mini-cover span {
  align-self: start;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.16);
  background: rgba(255, 255, 255, 0.08);
  padding: 4px 10px;
  font-size: 10px;
  letter-spacing: 0.18em;
}

.mini-cover--tall {
  height: 152px;
}

.mini-cover--rank {
  height: 120px;
}

.mini-cover--new {
  height: 148px;
}

.hero-tab {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.06);
  padding: 14px 16px;
  transition: all 0.2s ease;
}

.hero-tab--active {
  border-color: rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.12);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.05);
}

.tag-chip {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  border-radius: 999px;
  background: #f7ede4;
  padding: 0 12px;
  font-size: 12px;
  color: #8d6656;
}

.stat-block {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  border-radius: 20px;
  border: 1px solid #efe0d4;
  background: rgba(255, 255, 255, 0.7);
  padding: 14px 16px;
}

.stat-block span {
  font-size: 12px;
  color: #a17b69;
}

.stat-block strong {
  font-size: 15px;
  color: #2d211d;
}

.rank-number {
  display: inline-flex;
  height: 28px;
  width: 28px;
  align-items: center;
  justify-content: center;
  border: 1px solid transparent;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
}

.shelf-glyph {
  display: grid;
  height: 44px;
  width: 44px;
  place-items: center;
  border-radius: 16px;
  font-size: 18px;
  font-weight: 600;
}

.author-avatar {
  display: grid;
  height: 58px;
  width: 58px;
  min-width: 58px;
  place-items: center;
  border-radius: 18px;
  color: #fff;
  font-family: 'Iowan Old Style', 'Songti SC', serif;
  font-size: 20px;
  font-weight: 600;
}

.reveal-card {
  animation: reveal-up 0.55s ease both;
}

@keyframes reveal-up {
  from {
    opacity: 0;
    transform: translateY(18px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
