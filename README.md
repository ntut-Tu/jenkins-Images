# Jenkins Images

提供 `jenkins-config` 部署時使用的兩個 Docker 映像。

| 映像 | 內容 |
| --- | --- |
| `pdd-jenkins-controller` | Jenkins、固定版本的外掛；負責管理工作與建置紀錄 |
| `pdd-jenkins-agent` | 連線至 controller 的 Jenkins agent、Git、Docker CLI；執行 Pipeline 工作 |

測試使用的 Python 等環境由 `jenkins-pipelines` 的 Jenkinsfile 指定。

## 本機建置

需要 Docker。從本專案目錄執行：

```bash
docker build -t pdd-jenkins-controller:local -f controller/Dockerfile .
docker build -t pdd-jenkins-agent:local -f agent/Dockerfile .
```

要部署本機映像，將上述名稱填入 `jenkins-config/settings.local.yaml` 的
`images.controller` 與 `images.agent`，再執行該專案的 `./deploy.sh`。

## 自動建置與發布

| GitHub Actions 事件 | 結果 |
| --- | --- |
| Pull request、手動執行 | 建置並測試，不發布 |
| 推送 `main` | 建置受變更影響的映像；通過測試後發布 |
| 推送 `v*` 標籤 | 建置並發布兩個映像 |

映像發布至 GitHub Container Registry（GHCR）。`main` 使用 `v1.0.<執行序號>`；
`v*` Git 標籤使用同名映像標籤。此專案的映像名稱如下：

```text
ghcr.io/ntut-tu/pdd-jenkins-controller:<tag>
ghcr.io/ntut-tu/pdd-jenkins-agent:<tag>
```

## 測試

本機測試需要 Python 3.12 以上與 uv。

```bash
uv run --locked python -m unittest discover -s tests -v
```
