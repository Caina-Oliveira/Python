export interface IConnectionList {
  host: string;
  username: string;
  password: string;
  databaseName: string;
  prefix: string;
  writeMode: 'CSV' | 'JSON';
  maxRowsPerSize?: number;

  repositoryType: string;
  bucketName: string;
  fileKey: string;
  accessKey: string;
  secretAccessKey: string;
}

export interface IConnection {
  connectionList: IConnectionList[];
  fileList: any[];
  repositoryType: string;
  bucketName: string;
  fileKey: string;
  accessKey: string;
  secretAccessKey: string;
}
