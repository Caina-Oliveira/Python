import { CronJob } from 'cron';

import queue from '@config/queue';
import ConfigurationHandler from '@modules/configuration/ConfigurationHandler';
import ProcessorHandler from '@modules/processor/handlers/ProcessorHandler';

import { version } from '../../../package.json';

console.log(`current version ${version}`);

let semaphore = true;

(async () => {
  try {
    if (semaphore) {
      semaphore = false;

      const {
        data: { canExecute },
      } = await queue.patch<{ canExecute: boolean }>('queue', {
        id: `${process.env.INTEGRATION_KEY}`,
        ip: 'jolie',
        action: 'VERIFY',
      });

      console.log('Pode executar?', canExecute ? 'Sim' : 'Não');

      if (canExecute) {
        const configurationHandler = new ConfigurationHandler();

        const startProcessor = await configurationHandler.execute();

        if (startProcessor) {
          const processorHandler = new ProcessorHandler();

          await processorHandler.execute();
        }

        await queue.patch('queue', {
          id: `${process.env.INTEGRATION_KEY}`,
          ip: 'jolie',
          action: 'RELEASE',
        });
      }

      semaphore = true;
    }
  } catch (error) {
    console.log('🚀 ~ error:', error);
  }
})();
