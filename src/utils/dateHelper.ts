export function getDate(date: string): Date {
  if (date) {
    const [day, month, year] = date.replace('00:00:00', '').trim().split('/');

    return new Date(`${year}-${month}-${day}`);
  }

  console.log(date);
  return new Date();
}

export function getYear(date: Date): number {
  return date.getFullYear();
}

export function getMonth(date: Date): number {
  return date.getMonth() + 1;
}

export function getDay(date: Date): number {
  return date.getDate();
}

export function getDayOfWeek(date: Date): number {
  return date.getDay() + 1;
}

export function getFormattedDate(date: Date): string {
  return `${date.getFullYear()}-${date.getMonth() + 1 > 9 ? '' : 0}${date.getMonth() + 1}-${
    date.getDate() > 9 ? '' : 0
  }${date.getDate()}`;
}

export function getFormattedDateBr(date: Date): string {
  const month = date.getMonth() + 1;

  return `${date.getDate() < 9 ? 0 : ''}${date.getDate()}/${
    month < 9 ? 0 : ''
  }${month}/${date.getFullYear()}`;
}
