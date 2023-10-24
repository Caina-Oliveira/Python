import path from 'path';
import { chunk } from 'underscore';

import { IConnectionList } from '@modules/configuration/dtos/IConnection';
import writeFileSyncRecursive from '@utils/writeFileSyncRecursive';

import FileWriter from './FileWriter';

export default class JSONWriter extends FileWriter {
  public write(
    data: any[],
    outputDirectoryPath: string,
    filename: string,
    connection: IConnectionList,
    plusIndex = 0,
  ): void {
    let maxRowInFile = 100000;

    if (connection.maxRowsPerSize !== null && connection.maxRowsPerSize !== undefined) {
      maxRowInFile = connection.maxRowsPerSize;
    }

    const dataPerFile = chunk(data, maxRowInFile);

    dataPerFile.forEach((file, index) => {
      const content = JSON.stringify({ data: file });

      writeFileSyncRecursive(
        path.resolve(
          __dirname,
          outputDirectoryPath,
          JSONWriter.getFilename(filename, connection, index + plusIndex + 1),
        ),
        content,
      );
    });
  }
}
