import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';

import LogHandler from '@modules/log/LogHandler';

export default class ProcessorService {
  public async getStores(): Promise<any[]> {
    const files = fs.readFileSync(path.resolve('tmp', 'loja.json'));

    const stores = JSON.parse(files.toString());

    return stores || [];
  }

  public async getProducts(): Promise<any[]> {
    const files = fs.readFileSync(path.resolve('tmp', 'produto.json'));

    const products = JSON.parse(files.toString());

    return products || [];
  }

  public async getCost(): Promise<any[]> {
    const files = fs.readFileSync(path.resolve('tmp', 'custos.json'));

    const products = JSON.parse(files.toString());

    return products || [];
  }

  private runCommand(script: string, args: string[], log: LogHandler): Promise<string> {
    console.log(script, args.join(' '));
    return new Promise((resolve, reject) => {
      const child = spawn(script, args, {
        timeout: 2 * 60 * 60 * 1000,
        killSignal: 'SIGKILL',
      });

      let scriptOutput = '';

      child.stdout.setEncoding('utf8');

      child.stdout.on('data', (data) => {
        log.execute(`python: ${String(data).trimEnd()}`);

        scriptOutput += data.toString();
      });

      child.on('close', (code) => {
        console.log(`closing code: ${code}`);

        resolve(scriptOutput);
      });

      child.on('error', (err) => {
        reject(err.message);
      });
    });
  }

  public async getSales(init: string, end: string, log: LogHandler, module: string): Promise<void> {
    console.log(init, end, module);

    const [yearInit, monthInit, dayInit] = String(init).split('-');
    const [yearEnd, monthEnd, dayEnd] = String(end).split('-');

    try {
      await this.runCommand(
        'python3',
        [
          'python/main.py',
          `${dayInit}/${monthInit}/${yearInit}`,
          `${dayEnd}/${monthEnd}/${yearEnd}`,
          module,
        ],
        log,
      );
    } catch (error) {
      await log.execute(JSON.stringify(error));
    }
  }

  public async getValidacao(
    init: string,
    end: string,
    log: LogHandler,
    module: string,
  ): Promise<void> {
    console.log(init, end, module);

    const [yearInit, monthInit, dayInit] = String(init).split('-');
    const [yearEnd, monthEnd, dayEnd] = String(end).split('-');

    try {
      await this.runCommand(
        'python3',
        [
          'python/main.py',
          `${dayInit}/${monthInit}/${yearInit}`,
          `${dayEnd}/${monthEnd}/${yearEnd}`,
          module,
        ],
        log,
      );
    } catch (error) {
      await log.execute(JSON.stringify(error));
    }
  }

  public async getCompras(
    init: string,
    end: string,
    log: LogHandler,
    module: string,
  ): Promise<void> {
    console.log(init, end, module);

    const [yearInit, monthInit, dayInit] = String(init).split('-');
    const [yearEnd, monthEnd, dayEnd] = String(end).split('-');

    try {
      await this.runCommand(
        'python3',
        [
          'python/main.py',
          `${dayInit}/${monthInit}/${yearInit}`,
          `${dayEnd}/${monthEnd}/${yearEnd}`,
          module,
        ],
        log,
      );
    } catch (error) {
      await log.execute(JSON.stringify(error));
    }
  }

  public async getStock(log: LogHandler, module: string): Promise<void> {
    try {
      await this.runCommand('python3', ['python/main.py', `wylson`, `willytob`, module], log);
    } catch (error) {
      await log.execute(JSON.stringify(error));
    }
  }
}
