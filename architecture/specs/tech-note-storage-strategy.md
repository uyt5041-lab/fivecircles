# Tech Note: Image Storage & URL Management Strategy (MinIO)

## 1. Context
- 현재 `user-service`는 프로필 이미지 저장 시 MinIO를 사용 중임.
- 저장 시점에 **Presigned URL (7일 만료)**을 생성하여 DB에 저장하는 방식을 채택하고 있음.
- **문제점**: DB에 저장된 URL이 7일 후 만료되어 이미지가 표시되지 않는 이슈가 예상됨.

## 2. Discussion Points
드라마 포스터 및 캐릭터 이미지 관리 기능을 통합할 때 고려해야 할 두 가지 전략:

### Strategy A: On-demand URL Generation (추천)
- **방식**: DB에는 순수 파일명(Object Key)만 저장하고, API 요청 시점에 백엔드에서 짧은 만료 시간(예: 1시간)을 가진 Presigned URL을 생성하여 반환.
- **장점**: 보안성이 높고, URL 만료 이슈를 근본적으로 해결 가능.
- **고려사항**: 조회 요청마다 URL 생성 연산이 추가됨.

### Strategy B: Public Bucket Access
- **방식**: 특정 버킷(예: `public-assets`)을 Public Read로 설정하고 고정된 URL 형식을 사용.
- **장점**: 구현이 매우 단순하며, 브라우저 캐싱 활용에 유리함.
- **고려사항**: 비공개 이미지가 필요한 경우 별도의 버킷 관리가 필요함.

## 3. Recommendation for Admin Service
- **드라마/캐릭터 이미지**: 접근 제어가 필요 없는 공개 데이터이므로 **Strategy B(Public)** 방식이 관리 효율성 측면에서 유리해 보임.
- **사용자 프로필**: 개인정보 보호를 위해 **Strategy A(On-demand)** 방식으로 리팩토링하는 것을 권장.

---
*Last Updated: 2026-01-28 by Team B & Antigravity*
