/** Mock content mirrored from design-frontend for homework UI. */

export const currentIssue = {
  number: 14,
  period: '17–23 марта 2026',
  title: 'Новости DS для СВА',
  editor: 'Редакция Digest CDS',
  votingOpenUntil: '28 марта 2026',
}

/** Past published issue for archive demo (D-27 / ISSUE-04) — not current. */
export const pastIssue = {
  number: 13,
  period: '10–16 марта 2026',
  title: 'Прошлый выпуск · DS для СВА',
  editor: 'Редакция Digest CDS',
  items: [
    {
      slug: 'sql-dashboards',
      title: 'SQL-дашборды для аудиторской отчётности',
      position: 1,
      format: 'Статья',
      reading_minutes: 9,
      dek: 'Шаблоны витрин и дашбордов для ежемесячной отчётности аналитика СВА.',
    },
    {
      slug: 'prompt-engineering',
      title: 'Prompt Engineering Patterns 2026',
      position: 2,
      format: 'Статья',
      reading_minutes: 7,
      dek: 'Паттерны формулировок запросов к LLM для аудита.',
    },
  ],
}

export const materials = [
  {
    id: 'rag-systems',
    title: 'Building Production RAG Systems',
    dek: 'Как быстро находить нужные фрагменты регламентов СВА без ручного перебора документов.',
    format: 'Статья',
    readingMinutes: 8,
    date: '20 марта 2026',
    provenance: 'внешний текстовый источник',
    cover: '/covers/rag-systems.png',
    roles: ['ds', 'sva'],
    tags: ['RAG', 'LLM'],
    topic: 'ml-search',
    keywords: 'rag llm корпоративн документ поиск',
    snippet: 'Гибридный поиск по корпоративной базе знаний с reranking…',
    inIssue: true,
    issuePosition: 1,
    summary:
      'Статья описывает полный цикл построения RAG-системы для корпоративной базы знаний: ingestion, chunking, embedding, гибридный retrieval и reranking.',
    body: [
      'Для СВА наиболее релевантны сценарии поиска по регламентам, методологиям аудита и внутренним отчётам с цитированием источников.',
      'На этапе поиска система объединяет семантическое совпадение с точным совпадением терминов.',
    ],
    body_markdown: [
      '## Введение',
      '',
      'Для СВА наиболее релевантны сценарии поиска по регламентам, методологиям аудита и внутренним отчётам с цитированием источников.',
      '',
      '## Гибридный поиск',
      '',
      'На этапе поиска система объединяет семантическое совпадение с точным совпадением терминов.',
    ].join('\n'),
    related: [{ slug: 'anomaly-detection', title: 'Anomaly Detection in Audit Pipelines' }],
  },
  {
    id: 'empty-dek-article',
    title: 'Empty Dek Article',
    dek: '',
    format: 'Статья',
    readingMinutes: 3,
    date: '15 марта 2026',
    provenance: '',
    cover: '',
    roles: ['ds'],
    tags: [],
    topic: 'ml-search',
    keywords: 'empty dek',
    snippet: 'Fixture for D-36 empty dek.',
    inIssue: false,
    issuePosition: 99,
    summary: '',
    body: ['Fixture body without dek.'],
    body_markdown: '## Section One\n\nFixture prose without an audit dek.',
    related: [],
  },
  {
    id: 'anomaly-detection',
    title: 'Anomaly Detection in Audit Pipelines',
    dek: 'Как вовремя замечать аномалии в аудиторских выборках и сокращать ручную проверку.',
    format: 'Статья',
    readingMinutes: 5,
    date: '18 марта 2026',
    provenance: 'внутренний разбор',
    cover: '/covers/anomaly-detection.png',
    roles: ['analyst', 'sva'],
    tags: ['SQL', 'BI', 'аудит'],
    topic: 'reporting',
    keywords: 'sql дашборд аналитик отчётность bi reporting dashboard anomaly',
    snippet: 'Шаблоны витрин и дашбордов для ежемесячной отчётности аналитика СВА…',
    inIssue: true,
    issuePosition: 2,
    summary: 'Практики выявления аномалий в аудиторских пайплайнах на SQL и BI-витринах.',
    body: [
      'Материал показывает, как сочетать правила DQ и статистические сигналы без тяжёлого ML-стека.',
    ],
  },
  {
    id: 'langgraph-agents',
    title: 'LangGraph Multi-Agent Systems',
    dek: 'Как разделить сложную проверку на шаги с контролем и понятным итогом для аудитора.',
    format: 'Статья',
    readingMinutes: 12,
    date: '19 марта 2026',
    provenance: 'внешний текстовый источник',
    cover: '/covers/langgraph-agents.png',
    roles: ['ds'],
    tags: ['LangGraph', 'LLM'],
    topic: 'agents',
    keywords: 'langgraph агент multi-agent llm',
    snippet: 'Оркестрация агентов для многошаговых задач анализа данных…',
    inIssue: true,
    issuePosition: 3,
    summary: 'Оркестрация агентов для многошаговых проверок с явным контролем состояния.',
    body: ['Черновик для Data Scientist: границы ответственности агентов и точки эскалации.'],
  },
  {
    id: 'pgvector',
    title: 'pgvector for Enterprise Search',
    dek: 'PostgreSQL + pgvector как основа корпоративного семантического поиска.',
    format: 'Статья',
    readingMinutes: 6,
    date: '17 марта 2026',
    provenance: 'внешний текстовый источник',
    cover: '/covers/pgvector.png',
    roles: ['ds', 'sva'],
    tags: ['pgvector', 'RAG'],
    topic: 'ml-search',
    keywords: 'pgvector postgresql семантическ поиск rag',
    snippet: 'PostgreSQL + pgvector как основа корпоративного семантического поиска…',
    inIssue: true,
    issuePosition: 4,
    summary: 'Как поднять семантический поиск на PostgreSQL без отдельного vector DB.',
    body: ['Описаны индексы, ограничения и типовые ошибки эксплуатации в закрытом контуре.'],
  },
  {
    id: 'prompt-engineering',
    title: 'Prompt Engineering Patterns 2026',
    dek: 'Паттерны формулировок запросов к LLM для аудита.',
    format: 'Статья',
    readingMinutes: 7,
    date: '16 марта 2026',
    provenance: 'внешний текстовый источник',
    cover: '/covers/prompt-engineering.png',
    roles: ['analyst', 'sva'],
    tags: ['LLM', 'аудит'],
    topic: 'agents',
    keywords: 'prompt llm аудит формулировк',
    snippet: 'Чек-листы DQ и SQL-проверки полноты витрин перед отчётным циклом…',
    inIssue: true,
    issuePosition: 5,
    summary: 'Паттерны промптов для задач внутреннего аудита.',
    body: ['Фокус на воспроизводимости и проверке цитат, а не на «магии» модели.'],
  },
  {
    id: 'sql-dashboards',
    title: 'SQL-дашборды для аудиторской отчётности',
    dek: 'Шаблоны витрин и дашбордов для ежемесячной отчётности аналитика СВА.',
    format: 'Статья',
    readingMinutes: 9,
    date: '15 марта 2026',
    provenance: 'внутренний гайд',
    cover: '/covers/anomaly-detection.png',
    roles: ['analyst', 'sva'],
    tags: ['SQL', 'BI', 'аудит'],
    topic: 'reporting',
    keywords: 'sql дашборд аналитик отчётность bi',
    snippet: 'Шаблоны витрин и дашбордов для ежемесячной отчётности аналитика СВА…',
    inIssue: false,
    issuePosition: null,
    summary: 'Гайд для Data Analyst: витрины, KPI и контроль сроков отчётности.',
    body: ['Содержит примеры SQL и структуру дашборда цикла аудита.'],
  },
]

export const votingCycle = {
  label: 'Цикл голосования',
  period: '3–16 апреля 2026',
  closesOn: '16 апреля 2026',
  progressRatio: 0.55,
}

export const votingTopics = [
  {
    id: 'llm-audit',
    title: 'LLM для анализа аудиторских данных',
    materialsCount: 3,
    votes: 24,
    leading: false,
  },
  {
    id: 'rag-corp',
    title: 'RAG в корпоративной среде',
    materialsCount: 5,
    votes: 31,
    leading: true,
  },
  {
    id: 'automl-risk',
    title: 'AutoML для прогнозирования рисков',
    materialsCount: 2,
    votes: 18,
    leading: false,
  },
]

export function getMaterialById(id) {
  return materials.find((item) => item.id === id) ?? null
}

export function getIssueMaterials() {
  return materials
    .filter((item) => item.inIssue)
    .sort((a, b) => a.issuePosition - b.issuePosition)
}

/** Archive cards: past published only (excludes current — D-31). */
export function getArchiveIssues() {
  return [
    {
      number: pastIssue.number,
      period_label: pastIssue.period,
      title: pastIssue.title,
      material_count: pastIssue.items.length,
    },
  ]
}

/**
 * @param {number} number
 * @returns {import('../services/contentApi.js').IssueDto | null}
 */
export function getIssueByNumber(number) {
  const n = Number(number)
  if (n === currentIssue.number) {
    return {
      number: currentIssue.number,
      period_label: currentIssue.period,
      title: currentIssue.title,
      editor: currentIssue.editor,
      items: getIssueMaterials().map((m) => ({
        slug: m.id,
        title: m.title,
        position: m.issuePosition,
        format: m.format,
        reading_minutes: m.readingMinutes,
        dek: m.dek ?? null,
      })),
    }
  }
  if (n === pastIssue.number) {
    return {
      number: pastIssue.number,
      period_label: pastIssue.period,
      title: pastIssue.title,
      editor: pastIssue.editor,
      items: pastIssue.items.map((item) => ({ ...item })),
    }
  }
  return null
}
