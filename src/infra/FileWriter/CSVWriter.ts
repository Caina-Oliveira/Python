import path from 'path';

import { IConnectionList } from '@modules/configuration/dtos/IConnection';
import { toCSV } from '@utils/csvHelper';
import writeFileSyncRecursive from '@utils/writeFileSyncRecursive';

import FileWriter from './FileWriter';

export default class CSVWriter extends FileWriter {
  public write(
    data: any[],
    outputDirectoryPath: string,
    filename: string,
    connection: IConnectionList,
    plusIndex = 0,
  ): void {
    const content = toCSV(Array.isArray(data) ? data : [data]);

    writeFileSyncRecursive(
      path.resolve(outputDirectoryPath, CSVWriter.getFilename(filename, connection, 0 + plusIndex)),
      content,
    );
  }
}
