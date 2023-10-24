import { IConnectionList } from '@modules/configuration/dtos/IConnection';

export default abstract class FileWriter {
  public static getFilename(
    filename: string,
    connection: IConnectionList,
    indexFile: number,
  ): string {
    let extension = '';
    if (connection.writeMode != null && 'CSV'.includes(connection.writeMode.toUpperCase())) {
      extension = 'csv';
    } else {
      extension = 'json';
    }

    if (indexFile) return `${filename}.${connection.prefix}.${indexFile}.${extension}`;

    return `${filename}.${connection.prefix}.${extension}`;
  }

  public abstract write(
    data: any[] | any,
    outputDirectoryPath: string,
    filename: string,
    connection: IConnectionList,
    plusIndex?: number,
  ): void;
}
