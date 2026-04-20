# 📚 GrabLab 数据标准 Schema v1.0

> 所有平台爬虫输出数据统一遵循此标准

---

## 📱 自媒体内容数据标准

### 1. 基础视频数据结构

```json
{
  "video_id": "视频唯一标识",
  "platform": "平台名称（douyin/xiaohongshu/bilibili）",
  "search_keyword": "搜索关键词",
  "author": {
    "id": "作者ID",
    "name": "作者昵称",
    "fans_count": "粉丝数",
    "videos_count": "作品数",
    "verified": "是否认证"
  },
  "video_info": {
    "title": "视频标题",
    "description": "视频描述/文案",
    "duration": "视频时长（秒）",
    "publish_time": "发布时间",
    "cover_url": "封面图URL",
    "video_url": "视频链接",
    "tags": ["标签1", "标签2"]
  },
  "stats": {
    "view_count": "播放量",
    "like_count": "点赞数",
    "comment_count": "评论数",
    "share_count": "分享数",
    "collect_count": "收藏数",
    "forward_count": "转发数",
    "danmaku_count": "弹幕数"
  },
  "hot_score": "热度分值",
  "crawl_time": "抓取时间戳"
}
```

---

### 2. 深度内容分析结构

```json
{
  "content_analysis": {
    "category": "内容类别（教程/测评/Vlog/剧情等）",
    "theme": "主题标签",
    "keywords": ["关键词1", "关键词2", "关键词3"],
    
    "structure": {
      "hook": "开头钩子内容（前3秒）",
      "hook_type": "钩子类型（提问/冲突/悬念/数字/场景）",
      "main_content": "主体内容摘要",
      "climax_points": [
        {
          "timestamp": "时间点（秒）",
          "description": "高潮/转折点描述",
          "type": "类型（冲突/反转/干货/情绪）"
        }
      ],
      "ending": "结尾内容",
      "cta": "行动号召内容"
    },
    
    "pacing": {
      "avg_shot_duration": "平均镜头时长（秒）",
      "shot_count": "镜头切换次数",
      "pacing_rhythm": "节奏描述（快/中/慢）",
      "key_moments": [
        {
          "timestamp": "时间点",
          "event": "事件（转场/BGM变化/情绪点）"
        }
      ]
    },
    
    "visual": {
      "style": "画面风格（实拍/动画/混剪）",
      "color_tone": "色调",
      "text_overlays": [
        {
          "timestamp": "时间点",
          "text": "画面文字内容",
          "position": "位置"
        }
      ],
      "transitions": "转场方式",
      "special_effects": "特效使用"
    },
    
    "audio": {
      "bgm": {
        "name": "BGM名称",
        "mood": "情绪（欢快/悲伤/紧张等）",
        "beat_drops": ["BGM节拍高潮点时间"]
      },
      "voiceover": {
        "has_voiceover": "是否有旁白",
        "voice_type": "声音类型（男/女/童声/AI）",
        "speaking_speed": "语速（快/中/慢）",
        "tone": "语气（幽默/严肃/轻松）"
      },
      "sound_effects": ["音效列表"]
    },
    
    "script_structure": {
      "total_words": "总字数",
      "opening_words": "开头文案",
      "body_words": "主体文案",
      "closing_words": "结尾文案",
      "hooks_used": ["使用的钩子技巧"],
      "persuasion_techniques": ["说服技巧"]
    }
  }
}
```

---

### 3. 评论&弹幕分析结构

```json
{
  "comments": [
    {
      "id": "评论ID",
      "user_name": "用户名",
      "content": "评论内容",
      "like_count": "点赞数",
      "reply_count": "回复数",
      "time": "评论时间",
      "sentiment": "情感倾向（正面/负面/中性）",
      "is_hot": "是否热评"
    }
  ],
  
  "danmaku": [
    {
      "content": "弹幕内容",
      "time": "弹幕时间点（秒）",
      "count": "同类弹幕数量",
      "type": "弹幕类型（吐槽/互动/夸赞/质疑）"
    }
  ],
  
  "comment_analysis": {
    "total_count": "评论总数",
    "sentiment_distribution": {
      "positive": "正面比例",
      "negative": "负面比例",
      "neutral": "中性比例"
    },
    "hot_topics": ["评论高频话题"],
    "user_questions": ["用户提出的问题"],
    "user_pain_points": ["用户痛点"],
    "feature_requests": ["用户希望看到的内容"]
  }
}
```

---

## 🛒 电商商品数据标准

### 4. 商品基础数据结构

```json
{
  "product_id": "商品ID",
  "platform": "平台（xianyu/1688/pdd/taobao）",
  "category": {
    "level_1": "一级类目",
    "level_2": "二级类目",
    "level_3": "三级类目"
  },
  "product_info": {
    "title": "商品标题",
    "subtitle": "商品副标题",
    "description": "商品描述",
    "main_image": "主图URL",
    "detail_images": ["详情图URL列表"],
    "attributes": {
      "brand": "品牌",
      "model": "型号",
      "specifications": "规格参数"
    }
  },
  "price": {
    "current_price": "当前价格",
    "original_price": "原价",
    "price_history": [
      {
        "date": "日期",
        "price": "价格"
      }
    ]
  },
  "sales": {
    "monthly_sales": "月销量",
    "total_sales": "总销量",
    "sales_trend": "销量趋势（上升/下降/平稳）",
    "inventory": "库存状态"
  },
  "seller": {
    "id": "卖家ID",
    "name": "店铺名称",
    "rating": "店铺评分",
    "fans": "粉丝数",
    "location": "发货地",
    "is_verified": "是否认证商家",
    "response_rate": "回复率",
    "ship_speed": "发货速度"
  },
  "service": {
    "supports_7day_return": "支持7天退换",
    "supports_cod": "支持货到付款",
    "free_shipping": "是否包邮",
    "warranty": "保修政策"
  },
  "crawl_time": "抓取时间"
}
```

---

### 5. 批发供货数据结构

```json
{
  "wholesale": {
    "min_order": "起订量",
    "price_tiers": [
      {
        "quantity": "数量区间",
        "price": "单价"
      }
    ],
    "supports_dropship": "支持一件代发",
    "dropship_price": "代发价",
    "sample_available": "可拿样",
    "sample_price": "样品价",
    "customization": "支持定制",
    "moq_custom": "定制起订量",
    "lead_time": "发货周期",
    "factory_location": "工厂地址"
  }
}
```

---

### 6. 用户评价分析结构

```json
{
  "reviews": [
    {
      "id": "评价ID",
      "user_name": "用户名",
      "rating": "评分（1-5）",
      "content": "评价内容",
      "images": ["评价图片"],
      "time": "评价时间",
      "sku": "购买规格",
      "is_verified_purchase": "已验证购买",
      "seller_reply": "商家回复"
    }
  ],
  "review_analysis": {
    "total_count": "评价总数",
    "average_rating": "平均评分",
    "rating_distribution": {
      "5_star": "5星比例",
      "4_star": "4星比例",
      "3_star": "3星比例",
      "2_star": "2星比例",
      "1_star": "1星比例"
    },
    "pros": ["好评关键词/优点"],
    "cons": ["差评关键词/缺点"],
    "common_issues": ["常见问题"]
  }
}
```

---

### 7. 市场竞争分析结构

```json
{
  "market_analysis": {
    "competition_level": "竞争程度（高/中/低）",
    "price_range": {
      "min": "最低价",
      "max": "最高价",
      "median": "中位价",
      "average": "平均价"
    },
    "top_sellers": [
      {
        "seller_id": "卖家ID",
        "market_share": "市场份额",
        "price": "价格",
        "sales": "销量"
      }
    ],
    "trend": {
      "search_trend": "搜索趋势（上升/下降）",
      "seasonality": "季节性特征",
      "growth_rate": "增长率"
    }
  }
}
```

---

## 📊 平台榜单数据标准

### 8. 热搜榜数据结构

```json
{
  "platform": "平台名称",
  "crawl_time": "抓取时间",
  "hot_list": [
    {
      "rank": "排名",
      "keyword": "热搜关键词",
      "heat": "热度值",
      "trend": "趋势（新上榜/上升/下降）",
      "category": "分类",
      "related_topics": ["相关话题"],
      "content_count": "相关内容数量"
    }
  ]
}
```

---

### 9. 话题数据结构

```json
{
  "topic": {
    "id": "话题ID",
    "name": "话题名称",
    "description": "话题描述",
    "view_count": "浏览量",
    "discussion_count": "讨论数",
    "participant_count": "参与人数",
    "create_time": "创建时间",
    "category": "话题分类",
    "related_topics": ["相关话题"]
  }
}
```

---

## ✅ Schema 版本说明

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| v1.0 | 2026-04-20 | 初始版本，包含9大类标准数据结构 |
