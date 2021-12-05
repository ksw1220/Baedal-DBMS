# Application Development

## 목표

<code>seller.py</code>, <code>store.py</code>, <code>customer.py</code>, <code>delivery.py</code> 를 완성하세요.


자세한 내용은 pptx 참고

## Database Import

Database dump file (Postgres Costom format): ./baedal.dump

사용 방법: <code>baedal</code> database 만든 뒤, <code>pg_restore</code> 로 데이터베이스 복원

1. psql 로 db 접속하여 <code>baedal</code> database 생성
```bash
# Terminal/bash
psql -U postgres # 또는 자신 환경에 맞는 접속 방법. 동일하게 pg_restore 에도 사용
```

```psql
# psql
CREATE DATABASE baedal;
```

2. <code>pg_restore</code> 로 데이터베이스 복원

psql 이 사용하능한 위치에 baedal.dump 파일을 옮긴 뒤 복원 실행

제공된 docker 환경의 경우 <code>postgres-starter/pg_pgadmin/home</code> 로 파일을 옮기고 <code>docker exec</code> 명령어로 postgres 컨테이너에서 접속하면 <code>/home</code> 폴더 안에 baedal.dump 가 보일 것임.

```bash
pg_restore -U postgres -d baedal baedal.dump # -U postgres 대신에 자신의 DB 접속 정보 psql 과 동일하게 사용
```


## 제출물

- <code>project</code> 를 압축해서 제출하세요.
    - 압축은 .zip 또는 .tar 로만 압축하세요.
- 채점 기준 환경은 Linux 환경의 <code>Python 3.8</code> 입니다. (docker-compose.yml 환경과 동일)
