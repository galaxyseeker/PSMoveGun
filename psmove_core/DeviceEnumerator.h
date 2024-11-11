#ifndef DEVICE_ENUMERATOR_H
#define DEVICE_ENUMERATOR_H

class DeviceEnumerator {
public:
    virtual ~DeviceEnumerator() = default;
    virtual bool next() = 0;
    virtual bool valid() const = 0;
    virtual const char* get_path() const = 0;
    virtual int get_vendor_id() const = 0;
    virtual int get_product_id() const = 0;
};

#endif // DEVICE_ENUMERATOR_H
