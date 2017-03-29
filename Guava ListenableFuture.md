建议使用```ListenableFuture```全面替代```Future```，原因如下：

* ```ListenableFuture```包含```Future```的方法
* 后续的回调操作只会使用```ListenableFuture```，不提供```Future```相关的方法

## 接口
传统的```Future```在返回异步结果的时候，计算是否完成是不能确定的，所以还是存在 Block 的现象。
```ListenableFuture```允许你注册一个回调方法，当计算完成之后立即开始执行回调方法。这种扩展可以很高效地支持多种操作，而这些操作```Future```是不支持的。

增加回调方法的基本操作是调用```ListenableFuture```的```addListener(Runnable, Executor)```方法，指定在```Future```完成之后，在```Executor```中执行```Runnable```任务。
## 设置回调 
通常设置回调的方法我们会使用```Futures.addCallback(ListenableFuture<V>, FutureCallback<V>, Executor)```方法。其中```Futures```中实现了很多我们常用的功能方法（后面介绍），```FutureCallback```实现了两个方法：

* ```onSuccess(V)```：如果前一个```Future```执行成功，则基于结果执行该方法
* ```onFailure(Throwable)```：如果前一个```Future```执行失败，则基于异常执行该方法

## 创建
Guava 提供了```ListenableExecutorService```来把```ExecutorService```返回的```Future```转换成```ListenableFuture```。使用```MoreExecutors.listeningDecorator(ExecutorService)```把```ExecutorService```转换成```ListeningExecutorService```。

```java
ListeningExecutorService service = MoreExecutors.listeningDecorator(Executors.newFixedThreadPool(10));
ListenableFuture<Explosion> explosion = service.submit(new Callable<Explosion>() {
  public Explosion call() {
    return pushBigRedButton();
  }
});
Futures.addCallback(explosion, new FutureCallback<Explosion>() {
  // we want this handler to run immediately after we push the big red button!
  public void onSuccess(Explosion explosion) {
    walkAwayFrom(explosion);
  }
  public void onFailure(Throwable thrown) {
    battleArchNemesis(); // escaped the explosion!
  }
});
```
如果想设置或实现一个已经计算好的值，可以使用```AbstractFuture<V>```或者```SettableFuture```来定向处理。

如果必须把其他依赖的```Future```转换成```ListenableFuture```，那么就必须选择一个重量级的接口```JdkFutureAdapters.listenInPoolThread(Future)```。
## 应用
使用```Listenable```的一个更重要的原因就是它可以支持更复杂的异步操作链。

```java
ListenableFuture<RowKey> rowKeyFuture = indexService.lookUp(query);
AsyncFunction<RowKey, QueryResult> queryFunction =
  new AsyncFunction<RowKey, QueryResult>() {
    public ListenableFuture<QueryResult> apply(RowKey rowKey) {
      return dataService.read(rowKey);
    }
  };
ListenableFuture<QueryResult> queryFuture =
    Futures.transformAsync(rowKeyFuture, queryFunction, queryExecutor);
```
在```Futures```中支持很多对```ListenableFuture```的操作，而这些操作```Future```中是没有的。不同的操作需要不同的```Executors```来执行，一个```ListenableFuture```可以有多个行为在等待它。

在常用的场景中，我们希望一个```ListenableFuture```在某些其它任务完成之后开始计算，```Futures```提供了```Futures.allAsList```来实现：

* ```transformAsync(ListenableFuture<A>, AsyncFunction<A, B>, Executor)```：在 A 执行完成返回结果之后，异步执行```AsyncFunction<A, B>```返回 B
* ```transform(ListenableFuture<A>, Function<A, B>, Executor)```：在 A 执行完成返回结果之后，执行```Function<A, B>```返回 B
* ```allAsList(Iterable<ListenableFuture<V>>)```：在输入的所有任务成功完成之后，返回一个```ListenableFuture```并包含之前任务的结果；如果有任何一个任务失败或被取消，则返回的任务也立即失败或取消
* ```successfulAsList(Iterable<ListenableFuture<V>>)```在输入的所有任务成功完成之后，返回一个```ListenableFuture```并包含之前任务的结果；如果有任何一个任务失败或被取消，对应位置上的返回值为 null，注意这里无法区分是任务本身返回 null 还是任务失败导致返回 null。

```AsyncFunction<A, B>```提供了一个方法，```ListenableFuture<B> apply(A input)```。这个方法会异步地传递一个值。
## CheckedFuture
Guava 提供了```CheckedFuture<V, X extends Exception>```接口。这个接口是一个包含了可以获取异常的```ListenableFuture```。这使我们可以很方便地创建一个任务来获取在执行过程中抛出的异常逻辑。使用```Futures.makeChecked(ListenableFuture<V>, Function<Exception, X>)```来把一个```ListenableFuture```转换成```CheckedFuture```。