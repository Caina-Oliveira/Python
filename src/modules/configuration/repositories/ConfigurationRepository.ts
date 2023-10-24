import PouchDB from 'pouchdb';
import MemoryAdapter from 'pouchdb-adapter-memory';

import { IConfiguration } from '../dtos/IConfiguration';

PouchDB.plugin(MemoryAdapter);

export class ConfigurationRepository {
  private db: PouchDB.Database;

  constructor() {
    this.db = new PouchDB('skynet-configuration', { adapter: 'memory' });
  }

  public async save(configurations: IConfiguration[]): Promise<boolean> {
    const response = await Promise.all(
      configurations.map(async (config) => {
        const resp = await this.db.post(config);

        return resp;
      }),
    );

    return response.every(({ ok }) => ok);
  }

  public async getAll(): Promise<IConfiguration[]> {
    const response = await this.db.allDocs<IConfiguration>({ include_docs: true });

    const configurations: IConfiguration[] = response.rows.map((row) => ({
      module: row.doc?.module,
      connection: row.doc?.connection,
      parameters: row.doc?.parameters,
    }));

    return configurations;
  }

  public async destroy(): Promise<void> {
    await this.db.destroy();
  }
}
