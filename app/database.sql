drop database if exists blog;
create database blog;
use blog;

create table Roles(
id int primary key,
name varchar(255) not null,
permissions int not null
);

create table Users(
id int primary key,
role int not null,
email varchar(255) not null unique,
hashedPassword char(64) not null,
-- 昵称
name varchar(255) not null,
-- 创建日期
creationDate timestamp not null,
-- 个人简介
introduction varchar(255) not null,
-- 用户头像
-- 可为null，null时表示默认头像
profilePicture varchar(255),

foreign key(role) references Roles(id)
);

-- 文章的分类标签
-- tag创建后就不能删除
create table Tags(
id int primary key,
name char not null,
createUserId int not null,
creationDate timestamp not null default CURRENT_TIMESTAMP,

foreign key(createUserId) references Users(id)
);

-- 表示上传上来的原始文章的格式类型
create table OriginalArticleFormatType(
id int primary key,
-- 格式名
name char not null
);

-- 文章
create table Articles(
id int primary key,
-- 文章属主
userId int not null,
-- 因为需要经常查询用户名和用户头像所以做下冗余
userName varchar(255) not null,
userProfilePicture varchar(255) not null,
-- 文章标题
title varchar(255) not null,
-- 标识原始文章的数据格式
originalType int not null,
-- 原始内容简介
originalSummary char not null,
-- 原始文章内容
originalContent text not null,
-- 文章内容的第一章图片，在显示内容简介的时候可能会有用
firstContentPicture varchar(255),
-- 转化为html后的内容简介
summary char not null,
-- 转化为html后的文章内容
content text not null,
-- 创建时间
creationDate timestamp not null default CURRENT_TIMESTAMP,
-- 最后一次修改时间（第一次提交时等于creationDate）
lastModifiedDate timestamp not null default CURRENT_TIMESTAMP,
-- 点赞数目（每个用户只能一次）
likeCount int default 0,
-- 不喜欢的数目 (每个用户只能一次)
dislikeCount int default 0,
-- 浏览过的次数（一个用户的多次访问也记录）
viewedCount int default 0,
-- 评论数目
reviewCount int default 0,
-- 删除时并不真的删除，更改此标志，来控制
deleted bool not null default false,

foreign key(userId) references Users(id),
foreign key(originalType) references OriginalArticleFormatType(id)
);

create table ArticleTags(
articleId int not null,
tagId int not null,
-- 用来标识文章是否被删除，当文章被删除时，根据tag查看不应该看到相应的article
-- tag删除时仅需将记录从该表中删除即可
deleted bool not null default false,

primary key(articleId, tagId),
foreign key(articleId) references Articles(id),
foreign key(tagId) references Tags(id)
);

-- 评论
-- 暂时只支持纯文本
create table Reviews(
id int primary key,
userId int not null,
-- 用户信息适当冗余
userName varchar(255) not null,
userProfilePicture varchar(255) not null,

articleId int not null,
creationDate timestamp not null default CURRENT_TIMESTAMP,
content text not null,
-- 删除时并不真的删除，仅设置此标志，
-- 显示时可显示为一条评论已删除
deleted bool not null default false,

foreign key(userId) references Users(id),
foreign key(articleId) references Articles(id)
);

-- 针对评论的回复，暂时仅支持纯文本
-- 采用百度贴吧那种盖楼形式
create table Replies(
id int primary key,
reviewId int not null,

fromUserId int not null,
fromUserName varchar(255) not null,
fromUserProfilePicture varchar(255) not null,
toUserId int not null,
toUserName varchar(255) not null,
toUserProfilePicture varchar(255) not null,

creationDate timestamp not null default CURRENT_TIMESTAMP,
content text not null,
-- 回复的上一条评论，用来实现查看对话功能
pid int null,
-- 标识此回复是否被删除
deleted bool not null default false,

foreign key(reviewId) references Articles(id),
foreign key(fromUserId) references Users(id),
foreign key(toUserId) references Users(id),
foreign key(pid) references Replies(id)
);

-- 触发器用来保证用户信息的冗余数据在更新时一致
delimiter //
create trigger UpdateUserNameOrUserProfilePictureTrigger after update on Users
for each row
begin
    if new.name != old.name && new.profilePicture != old.profilePicture then
       update Articles set userName=new.name, userProfilePicture=new.profilePicture where Articles.userId = new.id;
       update Reviews set userName=new.name, userProfilePicture=new.profilePicture where Reviews.userId=new.id;
       update Replies set fromUserName=new.name, fromUserProfilePicture=new.profilePicture where Replies.fromUserId=new.id;
       update Replies set toUserName=new.name, toUserProfilePicture=new.profilePicture where Replies.toUserId=new.id;
    elseif new.name != old.name then
           update Articles set userName=new.name where Articles.userId = new.id;
           update Reviews set userName=new.name where Reviews.userId=new.id;
           update Replies set fromUserName=new.name where Replies.fromUserId=new.id;
           update Replies set toUserName=new.name where Replies.toUserId=new.id;
    elseif new.profilePicture != old.profilePicture then
           update Articles set userProfilePicture=new.profilePicture where Articles.userId = new.id;
           update Reviews set userProfilePicture=new.profilePicture where Reviews.userId=new.id;
           update Replies set fromUserProfilePicture=new.profilePicture where Replies.fromUserId=new.id;
           update Replies set toUserProfilePicture=new.profilePicture where Replies.toUserId=new.id;
    end if;
end //

-- 存储过程 用来获取对话中的评论
create procedure getCommentSession (in replyId int)
begin
    -- create temporary table res(fromUserName varchar(255), fromUserProfilePicture varchar(255),
    -- toUserName varchar(255), toUserProfilePicture varchar(255), creationTime timestamp,
    -- content text, deleted bool, pid int) ENGINE=MEMORY;
    -- declare parentId int;
    -- -- select pid into parentId from Replies where id=replyId;
    -- while parentId is not null do
    --       insert into res (select fromUserId, fromUserProfilePicture, toUserId, toUserProfilePicture,
    --       creationDate, deleted, pid from Replies where id=parentId);
    -- end while;
    declare parentIds varchar(4000);
    declare tempId int;
    declare sonIds varchar(4000);
    declare newSonIds varchar(4000);
    select '' into parentIds;
    select replyId into tempId;
    select '' into sonIds;
    select cast(replyId as char) into newSonIds;

    while null is not null do
        if parentIds = ''
        then
            select cast(tempId as char) into parentIds;
        else
            select concat(parentIds, ',', tempId) into parentIds;
        end if;
        select pid into tempId from Replies where id = tempId;
    end while;

    while newSondIds is not null do
        select concat(newSonIds, ',', sonIds) into newSonIds;
        select group_concat(id) into newSonIds from Replies where find_set(pid, newSonIds);
    end while;

    select fromUserName fromUserProfilePicutre, toUserName, toUserProfilePicture, creationDate,
    content, deleted bool from Replies where find_set(id, concat(parentIds, sonIds));

end //

delimiter ;
