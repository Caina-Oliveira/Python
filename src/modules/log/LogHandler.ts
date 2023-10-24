import api from '@config/skynet';

export default class LogHandler {
  public async execute(message: string): Promise<void> {
    console.log(message);

    await api.post(`open/logreceiver`, {
      systemName: 'Skynet Agent',
      logMessage: message,
      logCode: '2001',
      identificationName: '',
      identificationKey: process.env.INTEGRATION_KEY,
      version: '1.0.0',
    });
  }
}
