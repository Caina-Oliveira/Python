/* eslint-disable guard-for-in */
/* eslint-disable no-plusplus */
export function toCSV(objArray: any[]): string {
  let str = objArray.length ? `${Object.keys(objArray[0]).join(',')}\r\n` : '';

  for (let i = 0; i < objArray.length; i++) {
    let line = '';
    for (const index in objArray[i]) {
      if (line !== '') line += ',';

      line += objArray[i][index];
    }

    str += `${line}\r\n`;
  }

  return str;
}

export function toJSON(csv: string): any {
  const lines = csv
    .replace('sep=,', '')
    .replace(/(?<="[0-9]+)(,)(?=[0-9]+")/g, '.')
    .split('\n')
    .filter((line) => !!line.length);

  const result = [];

  const headers = lines[0].split(',');

  for (let i = 1; i < lines.length; i++) {
    const obj: { [key: string]: string } = {};
    const currentLine = lines[i].split(',');

    for (let j = 0; j < headers.length; j++) {
      obj[headers[j]] = currentLine[j].replace(/"/g, '');
    }

    result.push(obj);
  }

  return result;
}
