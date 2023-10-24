import fs from 'fs';
import path from 'path';

import api from '@config/skynet';
import getInstance from '@infra/FileWriter/getInstance';
import { IParameter } from '@modules/configuration/dtos/IConfiguration';
import { IConnectionList } from '@modules/configuration/dtos/IConnection';
import LogHandler from '@modules/log/LogHandler';
import { getFormattedDate } from '@utils/dateHelper';
import { uploadToS3 } from '@utils/s3Helper';
import { zipFolder } from '@utils/zipHelper';

import ProcessorService from '../services/ProcessorService';

export default class ExtractorHandler {
  private log: LogHandler;

  private service: ProcessorService;

  private module: string;

  private connection: IConnectionList;

  private parameters: IParameter[] = [];

  constructor(connection: IConnectionList, module: string, parameters: IParameter[]) {
    this.log = new LogHandler();

    this.service = new ProcessorService();

    this.module = module;
    this.connection = connection;
    this.parameters = parameters;
  }

  public async execute(): Promise<void> {
    try {
      await this.log.execute(`starting ${this.module}`);

      await this.log.execute('Loading lojas...');

      switch (this.module) {
        case 'IZICASH':
        case 'IZICASH_2':
        case 'COMPRAS':
          await this.izicashHandler();
          // await this.getCost();
          // await this.log.execute('Loading lojas...');
          // await this.getStores();
          // await this.getProducts();

          break;

        case 'IZILIVE':
          await this.iziliveHandler();
          break;
        case 'ESTOQUE':
          await this.log.execute('Loading estoque...');
          await this.getStock();
          break;

        default:
          break;
      }

      await this.saveParameters();

      await this.finish();
    } catch (error) {
      await this.log.execute(JSON.stringify(error));
    }
  }

  private async getProducts() {
    try {
      const products = await this.service.getProducts();

      await this.log.execute('Loaded produtos successfully!');

      const { writeMode } = this.connection;

      const fileWriter = getInstance(writeMode);

      await this.log.execute('saving produtos...');
      fileWriter.write(products, path.resolve('tmp', this.module), 'produto', this.connection);

      await this.log.execute('produtos saved');
    } catch (error) {
      await this.log.execute(JSON.stringify(error));
    }
  }

  private async izicashHandler() {
    await this.log.execute(`Loading ${this.module}...`);

    const [from, to] = this.getFromAndToDate();

    await this.getSales(from, to);
  }

  private async iziliveHandler() {
    await this.log.execute('Loading vendas...');

    const today = getFormattedDate(new Date());

    await this.getSales(today, today);
  }

  private async saveParameters() {
    const parameters = this.parameters.map((param) => ({ chave: param.name, valor: param.value }));

    const { writeMode } = this.connection;

    const fileWriter = getInstance(writeMode);

    await this.log.execute('saving parameters...');

    fileWriter.write(parameters, path.resolve('tmp', this.module), 'parameters', this.connection);

    await this.log.execute('parameters saved');
  }

  private async finish() {
    const files = fs.readdirSync(path.resolve('tmp', this.module));
    const dirPath = path.resolve('tmp', this.module);

    const fileKey = this.connection.fileKey.split('/');
    const filename = fileKey[fileKey.length - 1];

    await this.log.execute('Start compressing files...');

    await zipFolder(dirPath, files, filename);

    await this.log.execute('Files compressed successfully!');

    await this.log.execute('Start upload to S3...');

    const file = fs.readFileSync(path.resolve(dirPath, filename));

    console.log(file.byteLength);

    await uploadToS3(
      this.connection.accessKey,
      this.connection.secretAccessKey,
      this.connection.bucketName,
      this.connection.fileKey,
      file,
    );

    await this.log.execute('Files uploaded to S3 successfully!');

    await api.get(`service/company/finishupload?subproduct=${this.module}`);

    fs.rmdirSync('tmp', { recursive: true });
  }

  private async getStores() {
    try {
      const stores = await this.service.getStores();

      await this.log.execute('Loaded lojas successfully!');

      const { writeMode } = this.connection;

      const fileWriter = getInstance(writeMode);

      await this.log.execute('saving lojas...');
      fileWriter.write(stores, path.resolve('tmp', this.module), 'loja', this.connection);

      await this.log.execute('lojas saved');
    } catch (error) {
      await this.log.execute(JSON.stringify(error));
    }
  }

  private async getStock() {
    try {
      const stores = await this.service.getStock(this.log, this.module);

      await this.log.execute('Loaded estoque successfully!');

      const { writeMode } = this.connection;

      const fileWriter = getInstance(writeMode);

      await this.log.execute('saving estoque...');
      fileWriter.write(stores, path.resolve('tmp', this.module), 'estoque', this.connection);

      await this.log.execute('estoque saved');
    } catch (error) {
      await this.log.execute(JSON.stringify(error));
    }
  }

  private async getCost() {
    try {
      const cost = await this.service.getCost();

      await this.log.execute('Loaded custos successfully!');

      const { writeMode } = this.connection;

      const fileWriter = getInstance(writeMode);

      await this.log.execute('saving custos...');

      fileWriter.write(cost, path.resolve('tmp', this.module), 'custos', this.connection);

      await this.log.execute('custos saved');
    } catch (error) {
      await this.log.execute(JSON.stringify(error));
    }
  }

  private async getSales(start: string, end: string) {
    try {
      await this.log.execute(`Carregando de ${start} - ${end}`);
      await this.service.getSales(start, end, this.log, this.module);
      // const sales = await this.service.getSales(start, end, this.log, this.module);

      // console.log('🚀 vendas', sales.length);

      // const { writeMode } = this.connection;

      // const fileWriter = getInstance(writeMode);

      // await this.log.execute(`saving ${this.module}...`);

      // fileWriter.write(sales, path.resolve('tmp', this.module), 'vendas', this.connection);

      await this.log.execute(`${this.module} saved`);
    } catch (error) {
      await this.log.execute(JSON.stringify(error));
    }
  }

  private getFromAndToDate(): string[] {
    let from = '';
    let to = '';

    const dateBefore = this.parameters.find((param) => param.name === 'DATEBEFORE');

    if (!dateBefore || dateBefore.value === '0') {
      const yesterday = new Date();
      yesterday.setDate(yesterday.getDate() - 1);

      to = getFormattedDate(yesterday);
    } else {
      const [day, month, year] = dateBefore.value.split('/');

      const d = new Date(`${year}-${month}-${day} 00:00:00`);

      d.setDate(d.getDate() - 1);

      to = getFormattedDate(d);
    }

    const dateSince = this.parameters.find((param) => param.name === 'DATESINCE');

    if (!dateSince || dateSince.value === '0') {
      const dateIncremental = this.parameters.find((param) => param.name === 'DATAINCREMENTAL');

      if (!dateIncremental || dateIncremental.value === '0') {
        from = getFormattedDate(new Date());
      } else {
        const [day, month, year] = dateIncremental.value.split('/');

        from = `${year}-${month}-${day}`;
      }
    } else {
      const [day, month, year] = dateSince.value.split('/');

      from = `${year}-${month}-${day}`;
    }

    return [from, to];
  }
}
