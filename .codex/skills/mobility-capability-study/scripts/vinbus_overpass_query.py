from __future__ import annotations

def build_query(south, west, north, east):
    bbox = f'{south},{west},{north},{east}'
    return f'[out:json][timeout:180]; relation[route=bus][operator~VinBus,i]({bbox}); out tags geom;'

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--bbox', nargs=4, required=True)
    a = p.parse_args()
    print(build_query(*a.bbox))
