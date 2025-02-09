type ColumnType = "numerical" | "categorical";

export function determineColumnType(values: any[]): ColumnType {
  const cleanValues = values.filter((v) => v !== null && v !== undefined);
  if (cleanValues.length === 0) return "categorical";

  // 1. 먼저 수치형 데이터인지 확인
  const isNumber = cleanValues.every((value) => {
    const num = Number.parseFloat(value);
    return !isNaN(num) && isFinite(num);
  });

  if (isNumber) {
    // 숫자인 경우, 고유값의 수가 매우 적으면 범주형으로 간주
    const uniqueValues = new Set(cleanValues.map(Number.parseFloat));
    if (uniqueValues.size <= 3) {
      // 값이 3개 이하인 경우에만 범주형으로 간주
      return "categorical";
    }
    return "numerical";  // 대부분의 경우 수치형으로 간주
  }

  // 2. 날짜 데이터인지 확인
  const isDate = cleanValues.every((value) => {
    const date = new Date(value);
    return !isNaN(date.getTime());
  });

  if (isDate) {
    return "categorical";  // 날짜 데이터는 범주형으로 처리
  }

  // 3. 수치형/날짜형이 아니면 범주형으로 간주
  return "categorical";
}

export function preprocessData(data: any[], column: string) {
  if (!data.length) return { labels: [], values: [] };

  const values = data.map((row) => row[column]).filter((v) => v !== null && v !== undefined);

  if (determineColumnType(values) === "numerical") {
    // 수치형 데이터는 구간으로 나누기
    const numericValues = values.map((v) => Number.parseFloat(v));
    const min = Math.min(...numericValues);
    const max = Math.max(...numericValues);

    if (min === max) {
      // 모든 값이 동일한 경우 단일 카테고리로 처리
      return { labels: [`${min}`], values: [numericValues.length] };
    }

    const binCount = 10;
    const binSize = (max - min) / binCount;

    const bins = Array(binCount).fill(0);
    const labels = Array(binCount)
      .fill("")
      .map((_, i) => `${(min + i * binSize).toFixed(1)} - ${(min + (i + 1) * binSize).toFixed(1)}`);

    numericValues.forEach((value) => {
      const binIndex = Math.min(Math.floor((value - min) / binSize), binCount - 1);
      bins[binIndex]++;
    });

    return { labels, values: bins };
  } else {
    // 범주형 데이터는 각 카테고리의 빈도 계산
    const frequency: Record<string, number> = {};
    values.forEach((value) => {
      const key = String(value);
      frequency[key] = (frequency[key] || 0) + 1;
    });

    return {
      labels: Object.keys(frequency),
      values: Object.values(frequency),
    };
  }
}
