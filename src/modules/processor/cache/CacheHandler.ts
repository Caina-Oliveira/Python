import low, { LowdbSync } from 'lowdb';
import FileSync from 'lowdb/adapters/FileSync';

export interface IProduct {
  produtocodigo: string;
  produtonome: string;
  tipo: string;
  grupoprodutocodigo: string;
  grupoprodutonome: string;
  fornecedorcodigo: string;
  fornecedornome: string;
}

export interface IClientProvider {
  fornecedorcodigo: string;
  fornecedornome: string;
  clientecodigo: string;
  clientenome: string;
}

interface IDB {
  products: IProduct[];
  clients: IClientProvider[];
  salespeople: { vendedorcodigo: string; vendedornome: string }[];
}

export class CacheHandler {
  private db: LowdbSync<IDB>;

  constructor() {
    const adapter = new FileSync('db.json');

    this.db = low(adapter);

    this.db.defaults({ products: [], clients: [], salespeople: [] }).write();
  }

  getProduct(produtoCod: string): IProduct {
    const product = this.db.get('products').find((p) => p.produtocodigo === produtoCod);

    return product.value();
  }

  removeProducts(grupoprodutonome: string): void {
    console.log(this.db.get('products').value()[0]);

    this.db.get('products').remove({ grupoprodutonome }).write();

    console.log(this.db.get('products').value()[0]);
  }

  getProductByName(productName: string): IProduct {
    const product = this.db.get('products').find((p) => p.produtonome === productName);

    return product.value();
  }

  setProduct(product: IProduct): void {
    this.db.get('products').push(product).write();
  }

  bulkSetProducts(products: IProduct[]): void {
    this.db
      .get('products')
      .push(...products)
      .write();
  }

  getClientProvider(clientCod: string): IClientProvider {
    const client = this.db.get('clients').find((p) => p.clientecodigo === clientCod);

    return client?.value();
  }

  setClientProvider(clientProvider: IClientProvider): void {
    this.db.get('clients').push(clientProvider).write();
  }

  getSalesperson(personCod: string): { vendedorcodigo: string; vendedornome: string } {
    const salesPerson = this.db.get('salespeople').find((p) => p.vendedorcodigo === personCod);

    return salesPerson.value();
  }

  setSalesperson(salesPerson: { vendedorcodigo: string; vendedornome: string }): void {
    this.db.get('salespeople').push(salesPerson).write();
  }
}
