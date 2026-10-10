# 野獣邸 再現（Minecraft 統合版）
#   make        … パックと図を作り、dist/ にパックを置く
#   make test   … 自動テスト
#   make verify … 公式のブロック定義と突き合わせ直す（ネット接続が必要）

.PHONY: all build test verify clean

all: build

build:
	python3 build.py
	mkdir -p dist
	cp build/*.mcpack dist/

test:
	python3 -m pytest -q

verify:
	python3 -m tools.verify_blocks

clean:
	rm -rf build
