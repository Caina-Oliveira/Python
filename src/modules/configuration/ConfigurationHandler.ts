import api from '@config/skynet';
import LogHandler from '@modules/log/LogHandler';

import { IConnection } from './dtos/IConnection';
import { ConfigurationRepository } from './repositories/ConfigurationRepository';

interface IProductsResponse {
  resource: string[];
}

interface IConnectionsResponse {
  resource: IConnection;
}

interface IParametersResponse {
  resource: { name: string; value: string }[];
}

export default class ConfigurationHandler {
  private log: LogHandler;

  private repo: ConfigurationRepository;

  constructor() {
    this.log = new LogHandler();
    this.repo = new ConfigurationRepository();
  }

  public async execute(): Promise<boolean> {
    try {
      await this.log.execute('getting products...');

      const {
        data: { resource: products },
      } = await api.get<IProductsResponse>('service/etl/products');

      await this.log.execute(`loaded products ${JSON.stringify(products)}`);

      if (!products.length) return false;

      await this.log.execute('getting connections...');

      let configurations = await Promise.all(
        products.map(async (product) => {
          try {
            const { data: connection } = await api.post<IConnectionsResponse>(
              'service/etl/connectionsandfiles',
              {},
              {
                params: { product },
              },
            );

            const {
              resource: { connectionList },
            } = connection;

            return { connection: connectionList[0], module: product };
          } catch (error) {
            await this.log.execute(error);
            return { module: product };
          }
        }),
      );

      await this.log.execute(`connections loaded successfully`);

      await this.log.execute(`getting params ...`);

      configurations = await Promise.all(
        configurations.map(async (configuration) => {
          try {
            const { data: params } = await api.get<IParametersResponse>(
              'service/etl/queryparameters',
              {
                params: {
                  product: configuration.module,
                },
              },
            );

            return { ...configuration, parameters: params.resource };
          } catch (error) {
            await this.log.execute(error);
            return configuration;
          }
        }),
      );

      await this.repo.save(configurations);

      await this.log.execute(`params loaded successfully`);

      await this.log.execute(`save configuration on local db`);

      return true;
    } catch (error) {
      await this.log.execute(error);
      return false;
    }
  }
}
