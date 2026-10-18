// Transports : Bluetooth Low Energy (service UART Nordic, comme bleuart.cpp) et USB (Web Serial).

export const NUS_SERVICE = '6e400001-b5a3-f393-e0a9-e50e24dcca9e';
const NUS_RX = '6e400002-b5a3-f393-e0a9-e50e24dcca9e'; // écriture vers le VESC
const NUS_TX = '6e400003-b5a3-f393-e0a9-e50e24dcca9e'; // notifications du VESC

export class BleTransport {
  constructor() {
    this.name = 'Bluetooth';
    this.onData = () => {};
    this.onClose = () => {};
    this.device = null;
    this.rx = null;
    this.queue = Promise.resolve();
    this.chunk = 20; // même taille de bloc que VESC Tool
  }

  static get supported() {
    return typeof navigator !== 'undefined' && !!navigator.bluetooth;
  }

  async open() {
    this.device = await navigator.bluetooth.requestDevice({
      filters: [{ services: [NUS_SERVICE] }],
      optionalServices: [NUS_SERVICE],
    });
    this.name = this.device.name || 'VESC BLE';
    this.device.addEventListener('gattserverdisconnected', () => this.onClose());
    const server = await this.device.gatt.connect();
    const service = await server.getPrimaryService(NUS_SERVICE);
    this.rx = await service.getCharacteristic(NUS_RX);
    const tx = await service.getCharacteristic(NUS_TX);
    tx.addEventListener('characteristicvaluechanged', (ev) => {
      const v = ev.target.value;
      this.onData(new Uint8Array(v.buffer, v.byteOffset, v.byteLength));
    });
    await tx.startNotifications();
  }

  write(data) {
    // Les écritures GATT doivent être sérialisées, sinon le navigateur refuse « operation already in progress ».
    this.queue = this.queue.then(async () => {
      for (let i = 0; i < data.length; i += this.chunk) {
        const part = data.subarray(i, i + this.chunk);
        if (this.rx.writeValueWithoutResponse) await this.rx.writeValueWithoutResponse(part);
        else await this.rx.writeValue(part);
      }
    }).catch((e) => console.warn('BLE write', e));
    return this.queue;
  }

  async close() {
    if (this.device?.gatt?.connected) this.device.gatt.disconnect();
  }
}

export class SerialTransport {
  constructor() {
    this.name = 'USB';
    this.onData = () => {};
    this.onClose = () => {};
    this.port = null;
    this.reader = null;
    this.writer = null;
  }

  static get supported() {
    return typeof navigator !== 'undefined' && !!navigator.serial;
  }

  async open() {
    this.port = await navigator.serial.requestPort();
    await this.port.open({ baudRate: 115200 });
    this.writer = this.port.writable.getWriter();
    this.reader = this.port.readable.getReader();
    this._loop();
  }

  async _loop() {
    try {
      for (;;) {
        const { value, done } = await this.reader.read();
        if (done) break;
        if (value) this.onData(value);
      }
    } catch (e) {
      console.warn('Serial read', e);
    }
    this.onClose();
  }

  write(data) {
    return this.writer.write(data);
  }

  async close() {
    try {
      await this.reader?.cancel();
      this.reader?.releaseLock();
      this.writer?.releaseLock();
      await this.port?.close();
    } catch (e) {
      console.warn('Serial close', e);
    }
  }
}
