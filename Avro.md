Avro是一个数据序列化系统，提供：
* 丰富的数据类型
* 快速可压缩的二进制数据格式
* 持久化存储的文件容器
* RPC调用
* 与动态语言的轻量级结合。数据读写和RPC调用不需要生成额外代码。生成代码只作为静态语言的一个可选项。
## 创建Schema
Avro的schema是使用JSON定义的，由简单数据类型（null, boolean, int, long, float, double等）和复杂数据类型（record, enum, array, map, union, fixed）组成。下面是官方样例：user.avsc
[code]
{
    "namespace": "example.avro",
    "type": "record",
    "name": "User",
    "fields": [
        {"name": "name", "type": "string"},
        {"name": "favorite_number",  "type": ["int", "null"]},
        {"name": "favorite_color", "type": ["string", "null"]}
    ]
}
[/code]
一个record定义中中最少需要type、name和fields，也可以包括namespace和full name。在样例的User中，name的类型是String，而favorite_number和favorite_color的数据类型是union，Avro的union数据类型表示该字段的数据类型可以是JSON数组中的任意一个数据类型。这个例子中的union表示里面的值可以是int或null。
## 生成代码的序列化和反序列化
如果已经在pom.xml中加入了插件的话，直接使用mvn compile就可以把user.avsc在target中生成代码
[code]
<plugin>
    <groupId>org.apache.avro</groupId>
    <artifactId>avro-maven-plugin</artifactId>
    <version>1.7.7</version>
    <executions>
        <execution>
            <phase>generate-sources</phase>
            <goals>
                <goal>schema</goal>
                <goal>protocol</goal>
                <goal>idl-protocol</goal>
            </goals>
            <configuration>
                <sourceDirectory>${project.basedir}/src/main/avro/</sourceDirectory>
                <outputDirectory>${project.basedir}/src/main/java/</outputDirectory>
            </configuration>
        </execution>
    </executions>
</plugin>
[/code]
通过编译生成了User代码之后，就可以使用这个类创建对象了。Avro对象提供通过构造器或者Builder进行创建。Builder比使用构造器创建对象的优势在于会自动设置默认值，还有会验证数据类型。而构造器创建的对象只能到序列化的时候才能抛出异常。而构造器的优势在于比Builder的性能高一些，因为Builder在build的时候会创建一个备份写进去数据再返回。
[code lang="java"]
User user1 = new User();
user1.setName("Alyssa");
user1.setFavoriteNumber(256);
// Alternate constructor
User user2 = new User("Ben", 7, "red");
// Construct via builder
User user3 = User.newBuilder()
        .setName("Charlie")
        .setFavoriteColor("blue")
        .setFavoriteNumber(null)
        .build();
[/code]
创建好User之后，使用DatumWriter把Java对象转换成序列化格式的内存数据。SpecificDatumWriter类用来从User中获取schema和生成的类。DataFileWriter用来写序列化数据，包括创建文件、写入schema、写入数据，最后关闭文件。
[code lang="java"]
File file = new File("users.avro");
// Serialize user1, user2 and user3 to disk
DatumWriter<User> userDatumWriter = new SpecificDatumWriter<User>(User.class);
DataFileWriter<User> dataFileWriter = new DataFileWriter<User>(userDatumWriter);
dataFileWriter.create(user1.getSchema(), file);
dataFileWriter.append(user1);
dataFileWriter.append(user2);
dataFileWriter.append(user3);
dataFileWriter.close();
[/code]
反序列化跟序列换过程很相似。SpecificDatumReader对应SpecificDatumWriter，用来把序列化的数据转换成User，DatumReader对应DatumWriter用来读文件。接下来就是从DataFileReader中读取数据然后打印出来就可以了。
[code lang="java"]
// Deserialize Users from disk
DatumReader<User> userDatumReader = new SpecificDatumReader<User>(User.class);
DataFileReader<User> dataFileReader = new DataFileReader<User>(file, userDatumReader);
User user = null;
while (dataFileReader.hasNext()) {
    // Reuse user object by passing it to next(). This saves us from
    // allocating and garbage collecting many objects for files with
    // many items.
    user = dataFileReader.next(user);
    System.out.println(user);
}
[/code]
## 不生成代码的序列化和反序列化
因为Avro在数据中已经存储了schema信息，所以这意味着不管我们是否提前知道了schema，都可以通过读取序列化过的数据来获取schema，这样我们就可以不使用生成的代码来进行序列化和反序列化。
创建对象的时候不能再使用User类，而是使用通用的GenericRecord类，如果设置了不存在的字段会抛出AvroRuntimeException。
[code lang="java"]
Schema schema = new Schema.Parser().parse(new File("./src/main/avro/user.avsc"));
GenericRecord user1 = new GenericData.Record(schema);
user1.put("name", "Alyssa");
user1.put("favorite_number", 256);
// Leave favorite color null
GenericRecord user2 = new GenericData.Record(schema);
user2.put("name", "Ben");
user2.put("favorite_number", 7);
user2.put("favorite_color", "red");
[/code]
序列化过程和之前的过程区别在于，把User换成了GenericRecord，其他的完全一样。
[code lang="java"]
// Serialize user1 and user2 to disk
File file = new File("users.avro");
DatumWriter<GenericRecord> datumWriter = new GenericDatumWriter<GenericRecord>(schema);
DataFileWriter<GenericRecord> dataFileWriter = new DataFileWriter<GenericRecord>(datumWriter);
dataFileWriter.create(schema, file);
dataFileWriter.append(user1);
dataFileWriter.append(user2);
dataFileWriter.close();
[/code]
反序列化过程也与之前的过程相同，没有特别说明。
[code lang="java"]
// Deserialize users from disk
DatumReader<GenericRecord> datumReader = new GenericDatumReader<GenericRecord>(schema);
DataFileReader<GenericRecord> dataFileReader = new DataFileReader<GenericRecord>(file, datumReader);
GenericRecord user = null;
while (dataFileReader.hasNext()) {
    // Reuse user object by passing it to next(). This saves us from
    // allocating and garbage collecting many objects for files with
    // many items.
    user = dataFileReader.next(user);
    System.out.println(user);
}
[/code]
