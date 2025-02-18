export class ApiError extends Error {
    constructor(
      public status: number,
      message: string,
    ) {
      super(message);
      this.name = 'ApiError';
      // 이는 TypeScript에서 Error를 확장할 때 필요합니다.
      Object.setPrototypeOf(this, ApiError.prototype);
    }
  }
  