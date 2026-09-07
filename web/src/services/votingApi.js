import { delay } from '../utils/delay.js'

export class VoteSubmitError extends Error {
  constructor(message, { code = 'SUBMIT_FAILED', retryable = true } = {}) {
    super(message)
    this.name = 'VoteSubmitError'
    this.code = code
    this.retryable = retryable
  }
}

/**
 * Mock vote API. Fail-once can be armed via:
 * - `armFailNextVoteSubmit()` (tests / demos)
 * - URL `?simulateError=1` (handled by VotingPage before first submit)
 */
let failNextSubmit = false

export function armFailNextVoteSubmit() {
  failNextSubmit = true
}

export function resetVoteSubmitHarness() {
  failNextSubmit = false
}

export async function submitVote(topicId) {
  if (!topicId) {
    throw new VoteSubmitError('Выберите тему перед подтверждением голоса.', {
      code: 'NO_TOPIC',
      retryable: false,
    })
  }

  await delay()

  if (failNextSubmit) {
    failNextSubmit = false
    throw new VoteSubmitError(
      'Сервер голосования временно недоступен. Проверьте соединение и повторите попытку.',
      { code: 'NETWORK', retryable: true },
    )
  }

  return {
    topicId,
    savedAt: new Date().toISOString(),
  }
}
