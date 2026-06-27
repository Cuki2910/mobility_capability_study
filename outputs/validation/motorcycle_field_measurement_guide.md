# Huong dan do tay - Google Maps Android Motorcycle Mode

**Muc tieu**: do thoi gian xe may Google Maps cho 10 cap OD la **20 dia danh khac nhau**, khong dung centroid/diem khong ten.  
**Thiet bi**: Android co Google Maps va hien mode **Xe mo to hai banh**.  
**Thoi diem do**: uu tien ngay thuong 11h-14h de gan voi GTFS midday.  

## Cach do moi pair

1. Mo Google Maps -> Chi duong.
2. Nhap diem di va diem den bang **ten dia danh** trong bang duoi.
3. Neu Maps chon sai dia diem, dung toa do trong ngoac de doi chieu.
4. Chon mode **Xe mo to hai banh**.
5. Chup man hinh thay ro: origin, destination, mode xe may, so phut, gio do.
6. Gui anh theo so pair: `Pair 1`, `Pair 2`, ... Pair 0 da xong.

## Nguyen tac mau

- 10 OD pairs khac nhau.
- 20 dia danh distinct, moi dia danh chi xuat hien 1 lan.
- Mix healthcare / school / retail / park.
- Phu nhieu huong trong pilot area, khong lap VOP lam origin qua nhieu lan.

## 10 OD pairs can do

| # | Diem di | Diem den | Toa do diem di | Toa do diem den | Model motorcycle min | Google Maps motorcycle |
|---:|---|---|---|---|---:|---|
| 0 | Vinhomes Ocean Park | Tram y te xa Kieu Ky | 20.9929, 105.9451 | 20.9803277, 105.9586930 | 5.3 | 7 done |
| 1 | Benh vien Da khoa Gia Lam | Truong THPT Nguyen Van Cu | 21.0093912, 105.9440029 | 20.9816965, 105.9216683 | 9.4 | ____ |
| 2 | Brighton College Vietnam | The gioi di dong Da Ton | 20.9932061, 105.9390586 | 20.9861648, 105.9305191 | 5.4 | ____ |
| 3 | Vincom Mega Mall Ocean Park | Truong THCS Da Ton | 20.9939128, 105.9595355 | 20.9873768, 105.9326785 | 9.6 | ____ |
| 4 | Tram Y te xa Da Ton | Circle K Ocean Park | 20.9857635, 105.9312696 | 21.0014664, 105.9432461 | 6.2 | ____ |
| 5 | Greenfield School | Truong Tieu hoc Nong nghiep | 20.9749933, 105.9235567 | 21.0045269, 105.9385739 | 10.7 | ____ |
| 6 | Truong Tieu hoc Da Ton | AEON MaxValu Ocean Park | 20.9847081, 105.9377224 | 20.9932694, 105.9442984 | 3.7 | ____ |
| 7 | Gom Su Quang Minh | Tram y te thi tran Trau Quy | 20.9771711, 105.9237395 | 21.0079563, 105.9390378 | 11.6 | ____ |
| 8 | VinFast Ocean Park | Cong vien mua Ha | 20.9933776, 105.9601111 | 20.9713542, 105.9293674 | 13.0 | ____ |
| 9 | Trung tam iTplus | Zmart Ocean Park | 21.0088695, 105.93683 | 21.0011668, 105.9438902 | 4.8 | ____ |

## Neu Google Maps khong tim dung dia danh

- Thu bo dau tieng Viet.
- Neu co nhieu ket qua, chon ket qua gan toa do trong bang.
- Chi dung toa do khi named lookup sai/ambiguous; ghi note `searched by coordinate because named lookup ambiguous`.

## Sau khi ban gui anh

Toi se dien `google_maps_android_minutes`, lookup time, device notes, status; sau do tinh sai so model.