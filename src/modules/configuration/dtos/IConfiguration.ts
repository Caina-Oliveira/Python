import { IConnectionList } from './IConnection';

export interface IParameter {
  name: string;
  value: string;
}

export interface IConfiguration {
  module?: string;
  connection?: IConnectionList;
  parameters?: IParameter[];
}
