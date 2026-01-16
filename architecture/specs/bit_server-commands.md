# this document displays commands to control remote server (bit-ts)


ssh bit-ts 
= ssh -p 2222 <REMOTE_USER>@<REMOTE_IP>

# 접속
ssh bit-ts

# 원격에서 레포 상태 확인
ssh bit-ts "cd ~/nospoiler && git status"

# 원격 배포(서버에서 pull + compose)
ssh bit-ts "cd ~/nospoiler && git pull && docker compose up -d --build"

# alias

cat >> ~/.zshrc <<'EOF'
# nospoiler remote control (server: bit-ts, path: ~/nospoiler)
alias np-deploy="ssh bit-ts 'cd ~/nospoiler && git pull && docker compose up -d --build && docker compose ps'"
alias np-ps="ssh bit-ts 'cd ~/nospoiler && docker compose ps'"
alias np-logs="ssh bit-ts 'cd ~/nospoiler && docker compose logs --tail 200'"
alias np-logs-f="ssh bit-ts 'cd ~/nospoiler && docker compose logs -f --tail 200'"
alias np-test="ssh bit-ts 'cd ~/nospoiler && if docker compose config --services | grep -qx test; then docker compose run --rm test; else echo \"No test service in compose. Use: docker compose exec <service> <test-cmd>\"; docker compose config --services; fi'"


alias np-test="ssh bit-ts 'cd ~/nospoiler && ./gradlew test'"
alias np-test-info="ssh bit-ts 'cd ~/nospoiler && ./gradlew test --info'"

==
