import { ConfigurationRepository } from '@modules/configuration/repositories/ConfigurationRepository';
import LogHandler from '@modules/log/LogHandler';
import runPromisesSequentially from '@utils/runPromisesSequentially';

import ExtractorHandler from './ExtractorHandler';

export default class ProcessorHandler {
  private log: LogHandler;

  private repo: ConfigurationRepository;

  constructor() {
    this.log = new LogHandler();
    this.repo = new ConfigurationRepository();
  }

  public async execute(): Promise<void> {
    await this.log.execute('getting configuration...');

    const configurations = await this.repo.getAll();

    if (!configurations.length) return;

    await this.log.execute('loaded configuration successfully!');

    await runPromisesSequentially(
      configurations.map((config) => async () => {
        await this.log.execute(`Start processor to ${JSON.stringify(config.module)}`);

        if (!config?.connection) return new Promise<void>(() => console.log);

        const extractor = new ExtractorHandler(
          config.connection,
          config.module || '',
          config.parameters || [],
        );

        return extractor.execute();
      }),
    );

    this.repo.destroy();
  }
}
