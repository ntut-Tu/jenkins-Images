# Jenkins Images

此 repo 只建置 controller 與 agent 兩種映像，供 jenkins-config 從 GHCR 取得。現行架構依 REQ-002，沒有自訂 work 映像、SSH 工作服務或 CRD。

- Controller：Jenkins 2.568.3／Java 21，官方基底固定 digest；plugins.lock 固定完整相依，包括 Docker Pipeline、Kubernetes、JCasC、Job DSL、Git、JUnit。
- Agent：官方 inbound-agent／Java 21、Git，加入從官方 docker:28-cli 固定 digest 複製的 Docker CLI。以 jenkins UID 1000 執行，不安裝 Python 或測試套件。
- 測試映像：由 pipelines repo 的 Jenkinsfile 宣告官方 Python 映像，Docker Pipeline／Kubernetes plugin 管理其執行。不透過本 repo 建立通用 worker。
- 已驗證平台 Linux amd64；不宣稱多架構驗證。

## 本地建置

```bash
python3 -m unittest discover -s tests -v
docker build -t pdd-jenkins-controller:req002 -f controller/Dockerfile .
docker build -t pdd-jenkins-agent:req002 -f agent/Dockerfile .
```

Agent 的 Docker CLI 需要可用的 Docker daemon，連線與權限由 config repo 配置；K8s agent 不掛載 Docker socket。

## GHCR

GitHub Actions 在 main push 時先比較此次 push 前後的完整差異，再只建置受影響的映像：

| 變更路徑 | 建置映像 |
| --- | --- |
| controller/**、tools/**、tests/** | controller（包含外掛 lock、更新工具與其測試） |
| agent/** | agent |
| .dockerignore、.github/workflows/images.yaml | controller、agent |
| 只有 README 或其他無關檔案 | 不建置映像，只執行變更判斷 job |

刪除與跨目錄重新命名也計入；首次 push 或無法取得舊 commit 時建置兩者，避免漏掉建置。PR、手動執行及 v* tag 保留建置兩者的行為；main push 的受影響映像通過測試後會發布 GHCR，標籤為 `v1.0.<GitHub Actions run_number>`（例如 `v1.0.42`）；v* tag ref 發布對應版本標籤，不產生 hash 標籤。PR 及在 main 上手動執行僅建置測試，不發布。保留 provenance、SBOM；自動版本以 workflow 執行序號遞增，PR 或未建置映像的執行也會消耗序號，因此版號可能跳號；重跑同一次執行沿用相同版本。部署可使用版本標籤或 registry digest。版本 tag 不應覆寫。

```text
ghcr.io/<小寫 GitHub owner>/pdd-jenkins-controller:<tag>
ghcr.io/<小寫 GitHub owner>/pdd-jenkins-agent:<tag>
```

Workflow 使用 GITHUB_TOKEN packages:write；repo／組織需允許發布。私有映像的使用者需登入 GHCR，K8s 需 imagePullSecret。此交付未發布映像、建立遠端 repo 或 Git push。

## 外掛更新

controller/plugins.txt 是直接需要的外掛；plugins.lock 含完整必要相依。建置只使用 lock，不於 Jenkins UI／Helm 安裝另一套版本。取得官方 update-center JSON 快照後：

```bash
python3 tools/lock_plugins.py /path/to/update-center.actual.json
python3 -m unittest discover -s tests -v
```

審查 lock 差異、重建、執行 config repo 整合測試後再發布。下游可用最終 registry digest 固定交付內容；本地 image ID 不等於 registry manifest digest。

官方依據：[Docker Pipeline](https://www.jenkins.io/doc/book/pipeline/docker/)、[Inbound agent](https://github.com/jenkinsci/docker-agent)、[Kubernetes plugin](https://plugins.jenkins.io/kubernetes/)。
