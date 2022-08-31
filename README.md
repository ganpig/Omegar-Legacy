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

### 二、谱面文件（二进制格式，文件扩展名为 `.omgc`）

#### note 部分

该部分由一个整型数据 n（表示 note 总数）和 n 个 note 构成。

每个 note 所包含的数据如下：

- 轨道（取值范围 0~3）
- 点击时间（单位：ms）
- 结束时间（若大于点击时间则该 note 为长条）
- 初始速度（单位：pixel/s）

#### event 部分

该部分由一个整型数据 m（表示 event 总数）和 m 个 event 构成。

每个 event 由两个整型数据（时间、类型）和若干数据构成，具体类别如下：

**`0x01` 显示 note （即添加到渲染及判定列表）**

- note 编号（取值范围 0~(n-1)）

**`0x02` 更改 note 下落速度**

- note 编号（取值范围 0~(n-1)）
- 速度

### 三、歌曲信息文件（json 格式）

```json
{
	"name":"(曲名)",
	"composer":"(曲师)",
	"illustrator":"(曲绘画师)",
	"charts":
	[
		{
			"level":"Alpha",
			"difficulty":(定数),
			"by":"(谱师)",
			"md5":"(谱面文件的MD5码)"
		},
		{
			"level":"Beta",
			"difficulty":(定数),
			"by":"(谱师)",
			"md5":"(谱面文件的MD5码)"
		},
		......
	]
}
```

### 四、压缩包文件（zip 格式，文件扩展名为 `.omgz`）

- 歌曲信息文件：`info.json`
- 歌曲音频：`music.ogg`
- 曲绘：`illustration.png`
- `charts` 文件夹内的多个谱面文件： `(等级名称).omgc`
