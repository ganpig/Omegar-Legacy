# Omega-Charts-Creator

## 文件格式

### 一、制谱工程文件（json 格式）

```json
[
	{
		"name":"Section 1",
		"bpm":160,
		"start":1500, //单位:ms
		"notes":
		[
			{
				"track":0,
				"beat":[0,1], //分数
				"length":[0,1],
				"initialSpeed":500,
				"changeSpeed":[]
			},
			{
				"track":3,
				"beat":[2,1],
				"length":[3,2],
				"initialSpeed":500,
				"changeSpeed":[[[3,2],1500]]
			},
			......
		]
	},
	{
		"name":"Section 2",
		"bpm":180,
		"start":47000,
		"notes":[......]
	}
]
```

### 二、谱面文件（二进制格式，文件扩展名为 `.omgc`，c 代表 chart）

#### note 部分

该部分由一个整数 n（表示 note 总数）和 n 组 note 数据构成。

每组 note 数据如下：

- 轨道（取值范围 0~3）
- 点击时间（单位：ms）
- 结束时间（若大于点击时间则该 note 为长条）
- 初始速度（单位：pixel/s）

#### event 部分

该部分由一个整数 m（表示 event 总数）和 m 组 event 数据构成。

每组 event 数据包含两个整数（时间、类型）和若干参数，具体类型如下：

**`0x01` 显示 note （即添加到渲染及判定列表）**

- note 编号（取值范围 0~(n-1)）

**`0x02` 更改 note 下落速度**

- note 编号（取值范围 0~(n-1)）
- 速度

### 三、歌曲信息文件（文本格式，文件扩展名为 `.omgs`，s 代表 song）

前 3 行：3 个字符串，分别表示曲名、曲师、画师。

第 4 行：一个整数 n，表示谱面数量。

第 5 行起：n 组谱面信息。

每组谱面信息有 4 行，分别表示难度、定数、谱师、谱面文件 MD5 值。

### 四、压缩包文件（zip 格式，文件扩展名为 `.omgz`，z 代表 zip）

- 歌曲信息文件：`info.json`
- 歌曲音频：`music.ogg`
- 曲绘：`illustration.png`
- `charts` 文件夹内的多个谱面文件： `(等级名称).omgc`
